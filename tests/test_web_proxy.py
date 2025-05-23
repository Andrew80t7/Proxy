import unittest
from unittest.mock import patch, MagicMock
from web_proxy import app, rewrite_links


class TestWebProxy(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_rewrite_links(self):
        src = '<a href="/page">X</a>'
        out = rewrite_links(src, "http://ex.com", True, flag=1)
        # проверяем embed_ads в query
        self.assertIn('embed_ads=1', out)
        self.assertIn('url=http%3A%2F%2Fex.com%2Fpage', out)

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
