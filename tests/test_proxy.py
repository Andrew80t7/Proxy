import unittest
from Server.ProxyServer import ProxyServer


class DummySocket:
    def __init__(self):
        self._closed = False

    def fileno(self):
        return -1

    def close(self):
        self._closed = True


class FakeServer:
    """Сервер, у которого accept() бросает OSError."""

    def __init__(self):
        pass

    def accept(self):
        raise OSError("fail")

    def settimeout(self, t):
        pass

    def setsockopt(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        pass

    def listen(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def fileno(self):
        # чтобы select не включал его
        return -1


class TestProxyServer(unittest.TestCase):
    def setUp(self):
        # поднимаем сервер на свободном порту 0
        self.srv = ProxyServer('127.0.0.1', 0)

    def tearDown(self):
        self.srv.shutdown()

    def test_init_and_shutdown(self):
        self.assertTrue(self.srv.running)
        self.srv.shutdown()
        self.assertFalse(self.srv.running)

    def test_cleanup_inactive(self):
        dummy = DummySocket()
        self.srv.input_list.append(dummy)
        # форсим необходимость очистки
        self.srv.last_cleanup -= 100
        self.srv._cleanup_inactive_connections()
        self.assertNotIn(dummy, self.srv.input_list)

    def test_on_accept_error(self):
        # Подменяем server на объект, у которого accept() падает
        fake = FakeServer()
        # Заменяем и в input_list
        self.srv.input_list[0] = fake
        self.srv.server = fake

        # Теперь при вызове on_accept() не должно быть исключений
        try:
            self.srv.on_accept()
        except Exception as e:
            self.fail(f"on_accept() не должна выбрасывать, но выбросила: {e}")


if __name__ == "__main__":
    unittest.main()
