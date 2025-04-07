import requests
import sys
from Logs.logger import get_logger

logger = get_logger()

# Настройки прокси
proxies = {
    "http": "http://localhost:8080",
    "https": "http://localhost:8080",
}


def test_https_request():
    """Тестирование HTTPS-запроса через прокси"""
    url = "https://google.com/"
    try:
        logger.info(f"Отправка HTTPS-запроса к {url}")
        response = requests.get(url, proxies=proxies, timeout=10)
        logger.info(f"HTTPS-запрос успешен! Статус код: {response.status_code}")
        logger.debug(f"Часть ответа: {response.text[:200]}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка HTTPS-запроса: {e}")
        return False


def test_http_request():
    """Тестирование HTTP-запроса через прокси"""
    url = "http://example.com/"
    try:
        logger.info(f"Отправка HTTP-запроса к {url}")
        response = requests.get(url, proxies=proxies, timeout=10)
        logger.info(f"HTTP-запрос успешен! Статус код: {response.status_code}")
        logger.debug(f"Часть ответа: {response.text[:200]}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка HTTP-запроса: {e}")
        return False


def main():
    """Основная функция для тестирования прокси"""
    logger.info("Начало тестирования прокси-сервера")

    # Тестируем HTTP-запрос
    http_success = test_http_request()

    # Тестируем HTTPS-запрос
    https_success = test_https_request()

    # Выводим общий результат
    if http_success and https_success:
        logger.info("Все тесты успешно пройдены!")
        return 0
    else:
        logger.error("Некоторые тесты не пройдены!")
        return 1


if __name__ == '__main__':
    sys.exit(main())

# тесты,логи, подключение к браузеру
