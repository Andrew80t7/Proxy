import socket
import time
import select

from Connection.Forward import Forward

# Размер буфера
BUFFER_SIZE = 4096

# Задержка
DELAY = 0.0001


def modify_request(data: bytes):
    """
    Преобразует абсолютный URL в относительный путь.

    """
    try:
        lines = data.split(b'\r\n')
        if not lines:
            return data

        first_line = lines[0].decode('utf-8', errors='ignore')
        parts = first_line.split(' ')
        if len(parts) < 3:
            return data
        method, url, protocol = parts

        if url.startswith(("http://", "https://")):
            pos = url.find('/', url.find("://") + 3)
            path = url[pos:] if pos != -1 else "/"
            new_first_line = f"{method} {path} {protocol}"
            lines[0] = new_first_line.encode('utf-8')
            new_data = b'\r\n'.join(lines)

            return new_data
        return data

    except UnicodeError:
        return data


def parse_request(data: bytes):
    """
    Извлекает метод, хост и порт.

    """
    lines = data.split(b'\r\n')

    if not lines:
        return None, None, None

    first_line = lines[0].decode('utf-8', errors='ignore')
    parts = first_line.split(' ')

    if len(parts) < 2:
        return None, None, None

    method = parts[0]

    if method == 'CONNECT':

        host_port = parts[1].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 443
        return 'CONNECT', host, port

    else:
        for line in lines[1:]:
            if line.lower().startswith(b'host:'):
                host_port = line.split(b':', 1)[1].strip().decode('utf-8', errors='ignore')
                if ':' in host_port:
                    host, port = host_port.split(':')
                    port = int(port)
                else:
                    host = host_port
                    port = 80
                return method, host, port
        return None, None, None


class TheServer:
    """
    Основной класс сервера

    """

    def __init__(self, host: str, port: int):
        """
        Инициализирует прокси-сервер.

        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)
        self.input_list = [self.server]
        self.channel = {}

    def main_loop(self):
        """Основной цикл обработки событий сервера."""
        while True:
            time.sleep(DELAY)
            input_ready, _, _ = select.select(self.input_list, [], [], 0)
            for s in input_ready:
                if s == self.server:
                    self.on_accept()
                else:
                    self.on_recv(s)

    def on_accept(self):
        """
        Обрабатывает новое клиентское подключение.
        """
        clientsock, clientaddr = self.server.accept()
        print(f"{clientaddr} подключился")
        self.input_list.append(clientsock)
        self.channel[clientsock] = {'peer': None, 'parse': True, 'type': None}

    def on_recv(self, s: socket.socket):
        """
        Обрабатывает данные от клиента или сервера.

        """

        data = s.recv(BUFFER_SIZE)
        if not data:
            self.on_close(s)
            return

        if s in self.channel and self.channel[s]['parse']:
            method, host, port = parse_request(data)
            if method and host and port:
                forward = Forward().start(host, port)
                if forward:
                    self._setup_forward_connection(s, forward, method, data)
                else:
                    self._handle_connection_error(host, port, s)
            else:
                self._handle_invalid_request(s)
        else:
            self._forward_data(s, data)

    def _setup_forward_connection(self, s: socket.socket, forward: socket.socket, method: str, data: bytes):
        """
        Настраивает соединение с целевым сервером.
        """
        self.channel[s]['peer'] = forward
        self.channel[forward] = {'peer': s, 'parse': False, 'type': method}

        if method == 'CONNECT':
            self._handle_https_connection(s)
        else:
            self._handle_http_connection(s, forward, data)

    def _handle_https_connection(self, s: socket.socket):
        """
        Обрабатывает HTTPS-соединение
        """
        s.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        self.channel[s]['type'] = 'CONNECT'
        self.channel[s]['parse'] = False
        self.input_list.append(self.channel[s]['peer'])

    def _handle_http_connection(self, s: socket.socket, forward: socket.socket, data: bytes):
        """
        Обрабатывает HTTP-соединение.
        """
        new_data = modify_request(data)
        forward.send(new_data)
        self.channel[s]['type'] = 'HTTP'
        self.channel[s]['parse'] = False
        self.input_list.append(forward)

    def _handle_connection_error(self, host: str, port: int, s: socket.socket):
        """
        Обрабатывает ошибку подключения.
        """
        print(f"Не удалось подключиться к {host}:{port}")
        self.on_close(s)

    def _handle_invalid_request(self, s: socket.socket):
        """
        Обрабатывает некорректный запрос.
        """
        self.on_close(s)

    def _forward_data(self, s: socket.socket, data: bytes):
        """
        Перенаправляет данные между клиентом и сервером.
        """
        if s in self.channel and self.channel[s]['peer']:
            self.channel[s]['peer'].send(data)

    def on_close(self, s: socket.socket):
        """
        Закрывает соединение и освобождает ресурсы.

        """
        if s in self.input_list:
            print(f"{s.getpeername()} отключился")
            self.input_list.remove(s)
            if s in self.channel:
                self._cleanup_peer_connection(s)
            s.close()

    def _cleanup_peer_connection(self, s: socket.socket):
        """
        Очищает связанные соединения.
        """
        peer = self.channel[s]['peer']
        if peer and peer in self.input_list:
            self.input_list.remove(peer)
            peer.close()
        del self.channel[s]
        if peer in self.channel:
            del self.channel[peer]
