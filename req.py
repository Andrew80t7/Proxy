import requests

proxies = {
    "http": "http://localhost:8080",
    "https": "http://localhost:8080",
}


def test_https_request():
    url = "https://google.com/"
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        print("HTTPS-запрос прошёл успешно!")
        print("Статус код:", response.status_code)

        print("Часть ответа:", response.text[:200])
    except requests.exceptions.RequestException as e:
        print("Ошибка HTTPS-запроса:", e)


if __name__ == '__main__':
    test_https_request()

# тесты,логи, подключение кбраузеру
