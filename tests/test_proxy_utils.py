import os
import re
import tempfile
import unittest
from datetime import datetime
import shutil

import Server.ProxyServer as ps


class TestProxyUtils(unittest.TestCase):
    def test_factorial(self):
        self.assertEqual(ps.factorial(0),
                         1)
        self.assertEqual(ps.factorial(5),
                         120)
        with self.assertRaises(ValueError):
            ps.factorial(-1)

    def test_is_palindrome(self):
        self.assertTrue(ps.is_palindrome("A man, a plan,"
                                         " a canal: Panama"))
        self.assertFalse(ps.is_palindrome("hello"))

    def test_is_prime(self):
        self.assertFalse(ps.is_prime(-1))
        self.assertFalse(ps.is_prime(0))
        self.assertFalse(ps.is_prime(1))
        self.assertTrue(ps.is_prime(2))
        self.assertTrue(ps.is_prime(13))
        self.assertFalse(ps.is_prime(15))

    def test_fibonacci(self):
        self.assertEqual(ps.fibonacci(0),
                         0)
        self.assertEqual(ps.fibonacci(1),
                         1)
        self.assertEqual(ps.fibonacci(7),
                         13)
        with self.assertRaises(ValueError):
            ps.fibonacci(-5)

    def test_reverse_string(self):
        self.assertEqual(ps.reverse_string("abc"),
                         "cba")
        self.assertEqual(ps.reverse_string(""),
                         "")

    def test_modify_html(self):
        html = (b"<html><head></head>"
                b"<body><div class='ad-container'>"
                b"Ad</div><p>Text</p>"
                b"</body></html>")
        cleaned, blocked = ps.modify_html(html)
        self.assertIn(b"<p>Text</p>",
                      cleaned)
        self.assertEqual(len(blocked),
                         1)
        self.assertEqual(blocked[0]["selector"],
                         ".ad-container")

    def test_is_ad_host(self):
        # temporarily modify AD_HOSTS_1
        original = set(ps.AD_HOSTS_1)
        ps.AD_HOSTS_1.clear()
        ps.AD_HOSTS_1.update({"example.com",
                              "ads.test"})
        self.assertTrue(ps.is_ad_host("example.com"))
        self.assertTrue(ps.is_ad_host("sub.ads.test"))
        self.assertFalse(ps.is_ad_host("notads.com"))
        ps.AD_HOSTS_1.clear()
        ps.AD_HOSTS_1.update(original)

    def test_modify_request(self):
        req = (b"GET http://example.com/path"
               b" HTTP/1.1\r\nHost:"
               b" example.com\r\n\r\n")
        modified = ps.modify_request(req)
        self.assertTrue(modified.startswith(b"GET"
                                            b" /path HTTP/1.1"))
        # non-absolute
        req2 = (b"GET /index HTTP/1.1\r\nHost:"
                b" example.com\r\n\r\n")
        self.assertEqual(
            ps.modify_request(req2), req2)

    def test_parse_request(self):
        data = (b"CONNECT"
                b" host.com:443 HTTP/1.1\r\nDummy:"
                b" x\r\n\r\n")
        m, h, p = ps.parse_request(data)
        self.assertEqual((m, h, p), ("CONNECT",
                                     "host.com",
                                     443))
        data2 = (b"GET / HTTP/1.1\r\nHost:"
                 b" host.com:8080\r\n\r\n")
        m2, h2, p2 = ps.parse_request(data2)
        self.assertEqual((m2, h2, p2), ("GET",
                                        "host.com",
                                        8080))
        # missing host
        data3 = (b"GET / HTTP/1.1\r\nOther:"
                 b" x\r\n\r\n")
        self.assertEqual(ps.parse_request(data3),
                         (None, None, None))

    def test_save_dump_creates_file(self):
        tmpdir = tempfile.mkdtemp()
        try:

            orig = ps.DUMP_DIR
            ps.DUMP_DIR = tmpdir
            data = b"hello"
            ps.save_dump(data, "test")
            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1)
            fn = files[0]
            self.assertTrue(fn.endswith("_test.dump"))
            content = open(os.path.join(tmpdir, fn),
                           "rb").read()
            self.assertIn(b"Direction: test",
                          content)
            self.assertTrue(content.endswith(data))
        finally:
            ps.DUMP_DIR = orig
            shutil.rmtree(tmpdir)


if __name__ == '__main__':
    unittest.main()
