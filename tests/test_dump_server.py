import os
import threading
import time
import unittest
from http.client import HTTPConnection

from Server.dump import DUMP_DIR, run_dump_server


# Меняем на ваш реальный модуль


class TestDumpServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Гарантируем чистоту папки
        if os.path.exists(DUMP_DIR):
            for fn in os.listdir(DUMP_DIR):
                os.remove(os.path.join(DUMP_DIR, fn))
        else:
            os.makedirs(DUMP_DIR)

        # Создаем тестовый файл в дамп-директории
        cls.test_filename = "hello.txt"
        with open(os.path.join(DUMP_DIR, cls.test_filename), "w", encoding="utf-8") as f:
            f.write("world")

        # Задаем фиксированный порт
        cls.port = 8001

        # Запускаем сервер в фоне
        cls.server_thread = threading.Thread(
            target=lambda: run_dump_server(port=cls.port),
            daemon=True,
        )
        cls.server_thread.start()
        # Небольшая задержка, чтобы сервер поднялся
        time.sleep(0.5)

    def tearDown(self):
        # Принудительно завершаем процесс тестового сервера
        # У вас run_dump_server блокирует в serve_forever,
        # поэтому, например, os._exit(0) или ctrl-c в реальном окружении.
        # Здесь просто оставляем daemon-поток умирать вместе с процессом.
        pass

    def test_directory_serving(self):
        conn = HTTPConnection("localhost", self.port, timeout=2)
        conn.request("GET", f"/{self.test_filename}")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        self.assertEqual(resp.status, 200)
        self.assertEqual(body, "world")

    def test_nonexistent_file(self):
        conn = HTTPConnection("localhost", self.port, timeout=2)
        conn.request("GET", "/no_such.txt")
        resp = conn.getresponse()
        self.assertEqual(resp.status, 404)

if __name__ == "__main__":
    unittest.main()
