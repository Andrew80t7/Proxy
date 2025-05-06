import unittest
import threading
import time
import requests
import sys
import os

from Logs.logger import get_logger
from Server.ProxyServer import (
    ProxyServer,
    modify_request,
    parse_request,
    modify_html,
    is_ad_host
)

logger = get_logger()

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


class TestProxyServer(unittest.TestCase):
    """Тесты для ProxyServer"""

    @classmethod
    def setUpClass(cls):
        cls.host = 'localhost'
        cls.port = 8080
        cls.server = ProxyServer(cls.host, cls.port)
        cls.thread = threading.Thread(target=cls.server.main_loop, daemon=True)
        cls.thread.start()
        # даём время подняться
        time.sleep(2)
        cls.proxies = {
            "http": f"http://{cls.host}:{cls.port}",
            "https": f"http://{cls.host}:{cls.port}",
        }
        logger.info("ProxyServer for tests started.")

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        logger.info("ProxyServer for tests stopped.")

    def test_http_through_proxy(self):
        """HTTP-запрос через прокси должен вернуть 200"""
        resp = requests.get("http://example.com", proxies=self.proxies, timeout=10)
        self.assertEqual(resp.status_code, 200)

    def test_https_through_proxy(self):
        """HTTPS-запрос через прокси должен вернуть 200"""
        resp = requests.get("https://example.com", proxies=self.proxies, timeout=10)
        self.assertEqual(resp.status_code, 200)

    def test_nonexistent_host(self):
        """Запрос к несуществующему хосту должен бросить исключение"""
        with self.assertRaises(requests.exceptions.RequestException):
            requests.get("http://nonexistent.invalid", proxies=self.proxies, timeout=5)

    def test_connect_timeout(self):
        """Таймаут соединения должен бросить ConnectTimeout или ReadTimeout"""
        with self.assertRaises((requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout)):
            # адрес, который не отвечает
            requests.get("http://10.255.255.1", proxies=self.proxies, timeout=1)


class TestUtilities(unittest.TestCase):
    """Тесты для утилитных функций прокси"""

    def test_parse_request_http(self):
        raw = b"GET http://foo.bar/baz HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
        method, host, port = parse_request(raw)
        self.assertEqual(method, "GET")
        self.assertEqual(host, "foo.bar")
        self.assertEqual(port, 80)

    def test_parse_request_connect(self):
        raw = b"CONNECT foo.bar:443 HTTP/1.1\r\nHost: foo.bar:443\r\n\r\n"
        method, host, port = parse_request(raw)
        self.assertEqual(method, "CONNECT")
        self.assertEqual(host, "foo.bar")
        self.assertEqual(port, 443)

    def test_modify_request_change(self):
        req = b"GET http://foo.bar/path HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
        mod = modify_request(req)
        self.assertIn(b"GET /path HTTP/1.1", mod)

    def test_modify_request_nochange(self):
        req = b"GET /already HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
        mod = modify_request(req)
        self.assertIn(b"GET /already HTTP/1.1", mod)

    def test_is_ad_host(self):
        from Server.ProxyServer import AD_HOSTS_1
        AD_HOSTS_1.clear()
        AD_HOSTS_1.add("ads.test.com")
        self.assertTrue(is_ad_host("ads.test.com"))
        self.assertTrue(is_ad_host("sub.ads.test.com"))
        self.assertFalse(is_ad_host("notads.test.com"))

    def test_modify_html_removal(self):
        # HTML с контейнером рекламы и img с ads в src
        html = b"<html><head></head><body><div class='ad-container'>X</div><img src='http://ads.test.com/a.jpg'/></body></html>"
        cleaned_bytes, blocked = modify_html(html, "http://example.com")
        cleaned = cleaned_bytes.decode("utf-8", errors="ignore")
        self.assertNotIn("ad-container", cleaned)
        self.assertNotIn("ads.test.com", cleaned)
        # Мы должны были заблокировать минимум 1 элемент
        self.assertGreaterEqual(len(blocked), 1)


if __name__ == "__main__":
    unittest.main()
