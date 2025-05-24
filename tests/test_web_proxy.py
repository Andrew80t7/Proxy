import unittest
from unittest.mock import patch, MagicMock
from web_proxy import (app,
                       rewrite_links,
                       sum_list,
                       is_palindrome,
                       is_even,
                       celsius_to_fahrenheit)


class TestSimpleFunctions(unittest.TestCase):

    def test_is_even(self):
        self.assertTrue(is_even(0))
        self.assertTrue(is_even(2))
        self.assertTrue(is_even(-4))
        self.assertFalse(is_even(3))
        self.assertFalse(is_even(-7))

    def test_is_palindrome(self):
        self.assertTrue(is_palindrome(""))
        self.assertTrue(is_palindrome("A"))
        self.assertTrue(is_palindrome("Madam"))
        self.assertTrue(is_palindrome("Was it a car or a cat I saw"))
        self.assertTrue(is_palindrome("А роза упала на лапу Азора"))
        self.assertFalse(is_palindrome("Hello"))
        self.assertFalse(is_palindrome("Python"))

    def test_sum_list(self):
        self.assertEqual(sum_list([]), 0)
        self.assertEqual(sum_list([1, 2, 3]), 6)
        self.assertEqual(sum_list([-1, 0, 1]), 0)
        self.assertAlmostEqual(sum_list([1.5, 2.5]), 4.0)
        self.assertEqual(sum_list([10, -5, 3, 2]), 10)

    def test_celsius_to_fahrenheit(self):
        self.assertEqual(celsius_to_fahrenheit(0),
                         32)
        self.assertEqual(celsius_to_fahrenheit(100),
                         212)
        self.assertEqual(celsius_to_fahrenheit(-40), -40)
        self.assertAlmostEqual(celsius_to_fahrenheit(36.6),
                               97.88, places=2)
        self.assertAlmostEqual(celsius_to_fahrenheit(20.5),
                               68.9, places=1)


class TestWebProxy(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_rewrite_links(self):
        src = '<a href="/page">X</a>'
        out = rewrite_links(src, "http://ex.com",
                            True, flag=1)
        # проверяем embed_ads в query
        self.assertIn('embed_ads=1', out)
        self.assertIn('url=http%3A%2F%2Fex.com%2Fpage',
                      out)

    @patch('web_proxy.requests.get')
    def test_proxy_html(self, mock_get):
        m = MagicMock()
        m.content = b"<html><body>Hi</body></html>"
        m.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = m

        rv = self.client.get('/?url=http://ex.com&flag=2')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b"Hi", rv.data)
        # все ссылки переписаны
        self.assertIn(b"embed_ads=1", rv.data)

    @patch('web_proxy.requests.get')
    def test_proxy_binary(self, mock_get):
        m = MagicMock()
        m.content = b"\x00\x01"
        m.headers = {'Content-Type': 'application/octet-stream'}
        mock_get.return_value = m

        rv = self.client.get('/?url=http://ex.com/file')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, b"\x00\x01")


if __name__ == "__main__":
    unittest.main()
