import unittest
import threading
import time
import requests
import sys
import os
from Logs.logger import get_logger
from Server.ProxyServer import ProxyServer

logger = get_logger()
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


class TestProxyServer(unittest.TestCase):
    """Тесты для прокси-сервера"""

    host: str
    port: int
    server: ProxyServer
    server_thread: threading.Thread
    proxies: dict

    @classmethod
    def setUpClass(cls):
        """Настройка тестового окружения"""
        cls.host = 'localhost'
        cls.port = 8080
        cls.server = ProxyServer(cls.host, cls.port)
        cls.server_thread = threading.Thread(target=cls.server.main_loop)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

        cls.proxies = {
            "http": f"http://{cls.host}:{cls.port}",
            "https": f"http://{cls.host}:{cls.port}",
        }

        logger.info("Тестовое окружение настроено")

    @classmethod
    def tearDownClass(cls):
        """Очистка после тестов"""
        try:
            logger.info("Завершение работы тестового сервера")
            cls.server.shutdown()
            cls.server_thread.join(timeout=5)
            logger.info("Тестовое окружение очищено")
        except Exception as e:
            logger.error(f"Ошибка при очистке тестового окружения: {e}")

    def test_http_request(self):
        """Тест HTTP-запроса через прокси"""
        try:
            logger.info("Запуск теста HTTP-запроса")
            response = requests.get("http://example.com", proxies=self.proxies, timeout=10)
            self.assertEqual(response.status_code, 200)
            logger.info("HTTP-тест успешно пройден")
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP-запрос не удался: {e}")
            self.fail(f"HTTP-запрос не удался: {e}")

    def test_https_request(self):
        """Тест HTTPS-запроса через прокси"""
        try:
            logger.info("Запуск теста HTTPS-запроса")
            response = requests.get("https://example.com", proxies=self.proxies, timeout=10)
            self.assertEqual(response.status_code, 200)
            logger.info("HTTPS-тест успешно пройден")
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTPS-запрос не удался: {e}")
            self.fail(f"HTTPS-запрос не удался: {e}")

    def test_invalid_host(self):
        """Тест запроса к несуществующему хосту"""
        logger.info("Запуск теста несуществующего хоста")
        with self.assertRaises(requests.exceptions.RequestException):
            requests.get("http://invalid-host-that-does-not-exist.com",
                         proxies=self.proxies, timeout=5)
        logger.info("Тест несуществующего хоста успешно пройден")

    def test_connection_timeout(self):
        """Тест таймаута соединения"""
        logger.info("Запуск теста таймаута соединения")
        try:
            requests.get("http://10.0.0.1", proxies=self.proxies, timeout=1)
            self.fail("Ожидалось исключение таймаута, но его не произошло.")
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            logger.info("Тест таймаута соединения успешно пройден")


if __name__ == '__main__':
    unittest.main()


# Дампы скачивание,
# блокировщик рекламы, встраиватель рекламы,
# всё прон --> администрация белого дома,
# все казики --> ссылки на телеграм канал матмеха

# Сайты казика взять с реестра рос.ком надзора