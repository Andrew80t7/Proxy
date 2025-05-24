import threading
import time
import unittest
import socket as real_socket

# импортируем сразу моду
import Connection.Forward as forward_mod

from Connection.Forward import Forward


class DummyServer(threading.Thread):
    def __init__(self, port, delay=0, accept=True):
        super().__init__(daemon=True)
        self.port = port
        self.delay = delay
        self.accept = accept
        self.sock = real_socket.socket(
            real_socket.AF_INET,
            real_socket.SOCK_STREAM)
        self.sock.setsockopt(real_socket.SOL_SOCKET,
                             real_socket.SO_REUSEADDR,
                             1)
        self.sock.bind(("localhost", port))
        self.sock.listen(1)

    def run(self):
        try:
            conn, _ = self.sock.accept()
            if self.delay:
                time.sleep(self.delay)
            if self.accept:
                conn.send(b"OK")
            conn.close()
        finally:
            self.sock.close()


class TestForward(unittest.TestCase):
    def setUp(self):
        forward_mod.socket = real_socket

    def test_successful_connect(self):
        """Если сервер слушает"""
        port = 9001
        srv = DummyServer(port, accept=True)
        srv.start()
        time.sleep(0.1)  # ждём, пока сервер запустится

        f = Forward()
        s = f.start("localhost", port)
        self.assertIsNotNone(s,
                             "Ожидался валидный сокет при"
                             " успешном соединении")
        s.close()

    def test_refused_connect(self):
        """Если на"""

        f = Forward()
        result = f.start("localhost", 9999)
        self.assertIsNone(result, "Ожидалось None "
                                  "при отказе в соединении")

    def test_timeout(self):
        f = Forward()
        f.timeout = 0.01
        # Используем IP, который не отвечает
        result = f.start(
            "10.255.255.1",
            65000)
        self.assertIsNone(
            result,
            "Ожидалось None при"
            " невозможности установить соединение"
            " в срок"
        )


if __name__ == "__main__":
    unittest.main()
