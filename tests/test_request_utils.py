import os
import shutil
import tempfile
import unittest
from Server.ProxyServer import (
    modify_html,
    is_ad_host,
    modify_request,
    parse_request,
    save_dump,
    AD_HOSTS_1,
)


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Подготовим чистый AD_HOSTS_1
        AD_HOSTS_1.clear()
        AD_HOSTS_1.add("ads.test.com")

        # Заменяем DUMP_DIR на временную папку
        from Server import ProxyServer
        self.tmpdir = tempfile.mkdtemp()
        ProxyServer.DUMP_DIR = self.tmpdir

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_modify_html_removes_ads_and_injects_style(self):
        html = (
            b"<html><head></head><body>"
            b"<div class='ad-container'>X</div>"
            b"<img src='http://ads.test.com/a.jpg'/></body></html>"
        )
        cleaned_bytes, blocked = modify_html(html)
        cleaned = cleaned_bytes.decode()
        # рекламы нет
        self.assertNotIn("ad-container", cleaned)
        self.assertNotIn("ads.test.com", cleaned)
        # стиль появился
        self.assertIn(".telegram-banner", cleaned)
        # два элемента заблокированы
        self.assertGreaterEqual(len(blocked), 2)

    def test_is_ad_host(self):
        self.assertTrue(is_ad_host("ads.test.com"))
        self.assertTrue(is_ad_host("sub.ads.test.com"))
        self.assertFalse(is_ad_host("foo.com"))

    def test_modify_request(self):
        req = b"GET http://foo.bar/path HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
        mod = modify_request(req)
        self.assertIn(b"GET /path HTTP/1.1", mod)
        # уже относительный
        req2 = b"GET /foo HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
        self.assertIn(b"GET /foo HTTP/1.1", modify_request(req2))
        # некодируемые байты — без изменений
        bad = b"\xff\xfe"
        self.assertEqual(modify_request(bad), bad)

    def test_parse_request(self):
        raw = b"GET http://a/b HTTP/1.1\r\nHost: a\r\n\r\n"
        m, h, p = parse_request(raw)
        self.assertEqual((m, h, p), ("GET", "a", 80))
        raw2 = b"CONNECT a:443 HTTP/1.1\r\nHost: a:443\r\n\r\n"
        self.assertEqual(parse_request(raw2), ("CONNECT", "a", 443))
        # без host
        self.assertEqual(parse_request(b"BAD\r\n\r\n"), (None, None, None))

    def test_save_dump(self):
        data = b"hello"
        save_dump(data, "req")
        # в папке должен быть один .dump
        files = os.listdir(self.tmpdir)
        self.assertEqual(len(files), 1)
        fn = files[0]
        self.assertTrue(fn.endswith("_req.dump"))
        content = open(os.path.join(self.tmpdir, fn), "rb").read()
        self.assertIn(b"Direction: req", content)


if __name__ == "__main__":
    unittest.main()
