import unittest
from Server.ProxyServer import (ProxyServer,
                                fibonacci,
                                is_prime,
                                is_palindrome,
                                factorial,
                                reverse_string, AD_HOSTS_1, is_ad_host, modify_html)


class DummySocket:
    def __init__(self):
        self._closed = False

    def fileno(self):
        return -1

    def close(self):
        self._closed = True


class FakeServer:

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


class TestHTMLUtils(unittest.TestCase):
    def test_modify_html_removal_and_style(self):
        html = (b"<html><head></head><body>"
                b"<div class='ad-container'>Ad"
                b"</div><p>Hello</p></body></html>")
        cleaned, blocked = modify_html(html)
        text = cleaned.decode('utf-8')
        self.assertNotIn('ad-container', text)
        self.assertIn('<style>', text)
        # blocked should contain one element
        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0]['selector'],
                         '.ad-container')


class TestAdHostUtils(unittest.TestCase):
    def test_is_ad_host(self):
        # clear and set
        AD_HOSTS_1.clear()
        AD_HOSTS_1.update({'ads.test.com'})
        self.assertTrue(is_ad_host('ads.test.com'))
        self.assertTrue(is_ad_host('sub.ads.test.com'))
        self.assertFalse(is_ad_host('example.com'))


class TestProxyServer(unittest.TestCase):

    def test_factorial_positive(self):
        self.assertEqual(
            factorial(0), 1)
        self.assertEqual(
            factorial(5), 120)

    def test_factorial_negative(self):
        with self.assertRaises(ValueError):
            factorial(-3)

    def test_is_palindrome(self):
        self.assertTrue(
            is_palindrome("A man, a plan, "
                          "a canal: Panama"))
        self.assertFalse(
            is_palindrome("Hello"))
        self.assertTrue(
            is_palindrome(""))

    def test_is_prime(self):
        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(13))
        self.assertFalse(is_prime(15))

    def test_fibonacci_valid(self):
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)
        self.assertEqual(fibonacci(7), 13)

    def test_fibonacci_negative(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)

    def test_reverse_string(self):
        self.assertEqual(reverse_string("abc"),
                         "cba")
        self.assertEqual(reverse_string(""),
                         "")

    def setUp(self):
        self.srv = ProxyServer('127.0.0.1',
                               0)

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
        fake = FakeServer()
        # Заменяем и в input_list
        self.srv.input_list[0] = fake
        self.srv.server = fake

        # Теперь при вызове on_accept() не должно б
        try:
            self.srv.on_accept()
        except Exception as e:
            self.fail(f"on_accept() "
                      f"не должна выбрасывать,"
                      f" но выбросила: {e}")


if __name__ == "__main__":
    unittest.main()
