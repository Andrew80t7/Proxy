import sys, os, argparse, traceback, logging
import enum, struct, socket, socketserver, select

###################################################################################################

SOCKET_TIMEOUT_SEC = 120
STREAM_BUFFER_SIZE = 4096


###################################################################################################

# SOCKS 4 / 4A (TCP)
# https://www.openssh.com/txt/socks4.protocol
# https://www.openssh.com/txt/socks4a.protocol

class SOCKS4_VER(enum.IntEnum):
    REQUEST = 0x04
    REPLY = 0x00


class SOCKS4_CMD(enum.IntEnum):
    # Establish a TCP/IP stream connection
    CONNECT = 0x01
    # Establish a TCP/IP port binding
    BIND = 0x02


class SOCKS4_REPLY(enum.IntEnum):
    # Request granted
    GRANTED = 0x5A
    # Request rejected or failed
    FAILED_OR_REJECTED = 0x5B
    # Request failed because client is not running identd (or not reachable from server)
    FAILED_NO_IDENTD = 0x5C
    # Request failed because client's identd could not confirm the user ID in the request
    FAILED_BAD_IDENTD = 0x5D


###################################################################################################

def recvall(sock, n, /):
    data, count = [], 0
    while count < n:
        packet = sock.recv(n - count)
        if not packet:
            raise EOFError(f'Read {count} bytes from socket, expected {n} bytes')
        data.append(packet)
        count += len(packet)
    return b''.join(data)


def recv_null_terminated_string(sock, /):
    data = []
    while True:
        char = recvall(sock, 1)
        if char == b'\x00':
            return b''.join(data).decode('utf-8')
        data.append(char)


###################################################################################################

def safe_recv(sock, buf, done, /):
    try:
        packet = sock.recv(STREAM_BUFFER_SIZE)
        if len(packet) > 0:
            buf += packet
        else:
            done = True
    except Exception as e:
        logging.warning(f'{str(e)}\n{traceback.format_exc()}')
        done = True
    return buf, done


def safe_send(sock, buf, done, /):
    try:
        bytes_sent = sock.send(buf)
        buf = buf[bytes_sent:]
    except Exception as e:
        logging.warning(f'{str(e)}\n{traceback.format_exc()}')
        done = True
    return buf, done


def safe_sendfinal(sock, buf):
    try:
        sock.sendall(buf)
    except:
        pass


###################################################################################################

class SOCKS4ProtocolError(Exception):
    pass


class SOCKS4Handler(socketserver.StreamRequestHandler):
    def tune_socket_options(self, sock, /):
        sock.settimeout(SOCKET_TIMEOUT_SEC)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def read_socks4_request(self):
        # fixed-length: VER(1), CMD(1), DSTPORT(2), DSTADDR(4)
        header = recvall(self.connection, 8)
        ver, cmd, dst_port = struct.unpack('!BBH', header[0: 4])
        dst_addr = socket.inet_ntop(socket.AF_INET, header[4: 8])

        if ver != SOCKS4_VER.REQUEST:
            raise SOCKS4ProtocolError(f'Unknown version: {ver}')
        if (cmd != SOCKS4_CMD.CONNECT) and (cmd != SOCKS4_CMD.BIND):
            raise SOCKS4ProtocolError(f'Unknown command: {cmd}')

        # variable-length: USERID, DOMAIN (optional)
        user_id = recv_null_terminated_string(self.connection)

        dst_domain = None  # SOCKS 4A
        if (header[4: 7] == b'\x00\x00\x00') and (header[7: 8] != b'\x00'):
            dst_domain = recv_null_terminated_string(self.connection)
            if len(dst_domain) == 0:
                raise SOCKS4ProtocolError(f'Empty domain field in SOCKS 4A request: {dst_addr}')

        return (ver, cmd, dst_port, dst_addr, user_id, dst_domain)

    def write_socks4_reply(self, status, addr='0.0.0.0', port=0, /):
        logging.debug(f'Reply: {status};{addr};{port}')
        reply = struct.pack('!BBH', SOCKS4_VER.REPLY, status, port)
        reply += socket.inet_pton(socket.AF_INET, addr)
        self.connection.sendall(reply)

    def get_stream_desc(self, socket_a, socket_b, /):
        addr_a, port_a = socket_a.getpeername()
        addr_b, port_b = socket_b.getpeername()
        return f'{addr_a}:{port_a} <--> {addr_b}:{port_b}'

    def stream_tcp(self, socket_a, socket_b, /):
        stream_info = self.get_stream_desc(socket_a, socket_b)
        logging.debug(f'Starting stream: {stream_info}')

        sockets_list = [socket_a, socket_b]
        buf_a2b, buf_b2a = b'', b''
        done = False

        while not done:
            read_ready, write_ready, _ = select.select(sockets_list, sockets_list, [], 0.5)

            if socket_a in read_ready:
                buf_a2b, done = safe_recv(socket_a, buf_a2b, done)
            if socket_b in read_ready:
                buf_b2a, done = safe_recv(socket_b, buf_b2a, done)

            if socket_a in write_ready:
                buf_b2a, done = safe_send(socket_a, buf_b2a, done)
            if socket_b in write_ready:
                buf_a2b, done = safe_send(socket_b, buf_a2b, done)

        logging.debug(f'Finalizing stream: {stream_info}')
        safe_sendfinal(socket_a, buf_b2a)
        safe_sendfinal(socket_b, buf_a2b)

        logging.debug(f'Stopped stream: {stream_info}')

    def handle(self):
        logging.info('Connection accepted: %s:%s' % self.client_address)

        reply_on_fail = True
        try:
            self.tune_socket_options(self.connection)

            (ver, cmd, dst_port, dst_addr, user_id, dst_domain) = self.read_socks4_request()
            logging.debug(f'Request: {ver};{cmd};{dst_port};{dst_addr};{user_id};{dst_domain}')

            if dst_domain:
                dst_addr = socket.gethostbyname(dst_domain)
                logging.debug(f'Resolved {dst_domain} into {dst_addr}')

            if cmd == SOCKS4_CMD.CONNECT:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dst_socket:
                    self.tune_socket_options(dst_socket)
                    dst_socket.connect((dst_addr, dst_port))
                    (bind_addr, bind_port) = dst_socket.getsockname()

                    reply_on_fail = False
                    self.write_socks4_reply(SOCKS4_REPLY.GRANTED, bind_addr, bind_port)
                    self.stream_tcp(self.connection, dst_socket)

            elif cmd == SOCKS4_CMD.BIND:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bind_socket:
                    self.tune_socket_options(bind_socket)

                    bind_addr = socket.gethostbyname(socket.gethostname())
                    bind_socket.bind((bind_addr, 0))  # any port
                    bind_socket.listen(1)
                    (bind_addr, bind_port) = bind_socket.getsockname()

                    self.write_socks4_reply(SOCKS4_REPLY.GRANTED, bind_addr, bind_port)
                    (peer_socket, (peer_addr, peer_port)) = bind_socket.accept()
                    with peer_socket:
                        self.tune_socket_options(peer_socket)

                        if dst_addr != peer_addr:
                            raise SOCKS4ProtocolError(f'Got connection from {peer_addr}; expected from {dst_addr}')

                        reply_on_fail = False
                        self.write_socks4_reply(SOCKS4_REPLY.GRANTED, peer_addr, peer_port)
                        self.stream_tcp(self.connection, peer_socket)

        except EOFError as e:
            logging.warning(f'{str(e)}\n{traceback.format_exc()}')
        except socket.gaierror:
            logging.warning(f'Unable to resolve domain: {dst_domain}')
            self.write_socks4_reply(SOCKS4_REPLY.FAILED_OR_REJECTED)
        except Exception as e:
            logging.warning(f'{str(e)}\n{traceback.format_exc()}')
            if reply_on_fail:
                self.write_socks4_reply(SOCKS4_REPLY.FAILED_OR_REJECTED)
        finally:
            logging.info('Connection terminated: %s:%s' % self.client_address)
            self.server.close_request(self.request)


###################################################################################################

def parse_args():
    parser = argparse.ArgumentParser(description='Simple SOCKS4 server')

    parser.add_argument('--log-level', action='store', type=str,
                        dest='log_level', default='DEBUG', help='Log level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('--log-path', action='store', type=str,
                        dest='log_path', default=None, help='Log file path')
    parser.add_argument('--host', action='store', type=str,
                        dest='host', default='127.0.0.1', help='Server IP or hostname')
    parser.add_argument('--port', action='store', type=int,
                        dest='port', default=1080, help='Port to listen')

    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_args()

        logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s',
                            level=logging.getLevelName(args.log_level.upper()), filename=args.log_path)
        logging.info(f'Starting server at {args.host}:{args.port}')

        with socketserver.ThreadingTCPServer((args.host, args.port), SOCKS4Handler) as server:
            server.serve_forever()  # interrupt with Ctrl+C
    except KeyboardInterrupt as e:
        logging.info('Shutting down')
        sys.exit(0)
    except Exception as e:
        logging.error(f'{str(e)}\n{traceback.format_exc()}')
        sys.exit(1)