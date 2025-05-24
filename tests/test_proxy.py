import unittest
from Server.ProxyServer import (ProxyServer,
                                fibonacci,
                                is_prime,
                                is_palindrome,
                                factorial,
                                reverse_string,
                                AD_HOSTS_1,
                                is_ad_host,
                                modify_html,
                                time_to_seconds,
                                is_prime_v2,
                                circle_area,
                                is_pangram,
                                count_words,
                                find_max,
                                is_leap_year,
                                km_to_miles,
                                sum_list,
                                is_even)


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
                b"</div>"
                b"<p>Hello</p></body></html>")

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
        self.assertTrue(
            is_ad_host('ads.test.com'))
        self.assertTrue(
            is_ad_host('sub.ads.test.com'))
        self.assertFalse(
            is_ad_host('example.com'))


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
        self.assertEqual(
            fibonacci(0), 0)
        self.assertEqual(
            fibonacci(1), 1)
        self.assertEqual(
            fibonacci(7), 13)

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
        try:
            self.srv.on_accept()
        except Exception as e:
            self.fail(f"on_accept() "
                      f"не должна выбрасывать,"
                      f" но выбросила: {e}")


class TestNewFunctions(unittest.TestCase):

    def test_is_even(self):
        self.assertTrue(is_even(0))
        self.assertTrue(is_even(-4))
        self.assertFalse(is_even(3))
        self.assertFalse(is_even(9999999))

    def test_sum_list(self):
        self.assertEqual(sum_list([1, 2, 3]), 6)
        self.assertEqual(sum_list([]), 0)
        self.assertAlmostEqual(sum_list([1.5, 2.5]), 4.0)
        self.assertEqual(sum_list([-10, 5]), -5)

    def test_km_to_miles(self):
        self.assertAlmostEqual(km_to_miles(1),
                               0.621371)
        self.assertAlmostEqual(km_to_miles(0),
                               0.0)
        self.assertAlmostEqual(km_to_miles(100),
                               62.1371)

    def test_is_leap_year(self):
        self.assertTrue(is_leap_year(2000))
        self.assertTrue(is_leap_year(2020))
        self.assertFalse(is_leap_year(1900))
        self.assertFalse(is_leap_year(2021))
        self.assertTrue(is_leap_year(2012))

    def test_find_max(self):
        self.assertEqual(find_max([3, 1, 4, 2]), 4)
        self.assertEqual(find_max([-5, -1, -10]), -1)
        self.assertIsNone(find_max([]))
        self.assertEqual(find_max([5.5, 3.3]), 5.5)

    def test_count_words(self):
        self.assertEqual(count_words("Hello world"), 2)
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("   Multiple   spaces   "), 2)
        self.assertEqual(count_words("No-spaces-here"), 1)

    def test_is_pangram(self):
        self.assertTrue(is_pangram("The quick brown"
                                   " fox jumps over the lazy dog"))
        self.assertFalse(is_pangram("Hello world"))
        self.assertTrue(is_pangram("Pack my box with"
                                   " five dozen liquor jugs"))
        self.assertFalse(is_pangram(""))

    def test_circle_area(self):
        self.assertAlmostEqual(circle_area(1),
                               3.14159,
                               places=4)
        self.assertAlmostEqual(circle_area(2.5),
                               19.6349375,
                               places=4)
        with self.assertRaises(ValueError):
            circle_area(-5)

    def test_time_to_seconds(self):
        self.assertEqual(time_to_seconds(1, 30),
                         5400)
        self.assertEqual(time_to_seconds(0, 45),
                         2700)
        self.assertEqual(time_to_seconds(2, 0),
                         7200)
        with self.assertRaises(ValueError):
            time_to_seconds(-1, 10)
        with self.assertRaises(ValueError):
            time_to_seconds(2, -5)

    def test_is_prime_v2(self):
        self.assertTrue(is_prime_v2(2))
        self.assertTrue(is_prime_v2(7919))
        self.assertFalse(is_prime_v2(1))
        self.assertFalse(is_prime_v2(4))
        self.assertFalse(is_prime_v2(-5))


if __name__ == "__main__":
    unittest.main()
