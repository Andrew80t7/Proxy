# Proxy Server на Python 🌊🔥⚡

Этот проект реализует низкоуровневый HTTP/HTTPS-прокси-сервер и веб-обёртку на Flask для фильтрации рекламы и вставки кастомных баннеров на посещаемых страницах.


* **Низкоуровневый прокси (порт 8080)**

  * Перехват и блокировка запросов к рекламным доменам (из `ad_hosts.txt`)
  * Перезапись HTTP-запросов для корректной работы через прокси
* **Веб-обёртка Flask (порт 5000)**

  * Получает очищенный HTML через прокси или напрямую
  * Удаляет рекламные теги и элементы из HTML
  * Переписывает все ресурсы (`href`, `src`) так, чтобы они шли через веб-прокси
  * Вставляет кастомные баннеры в начало `<body>`

## Структура проекта

```
project_root/
├── Server/ProxyServer.py   # Низкоуровневый прокси
├── Server/banners.py       # Логика выбора и генерации баннеров
├── ad_hosts.txt            # Список рекламных доменов для блокировки
├── web_proxy.py            # Flask-обёртка над прокси + вставка баннеров
├── tests/test_proxy.py     # Юнит-тесты для прокси и утилит
└── README.md               # Документация
```

## Требования

* Python 3.8+
* Библиотеки:

  * `requests`
  * `flask`
  * `beautifulsoup4`
  * `bs4`

Установить зависимости:

```bash
pip install -r requirements.txt
```

##  Запуск прокси и веб-сервиса

1. **Запустить низкоуровневый прокси** (на порту `8080`):

   ```bash
   python web_proxy.py  # в начале поднимается ProxyServer в потоке
   ```

2. **Запустить Flask-обёртку** (порт `5000`):

   Тот же скрипт `web_proxy.py` запускает оба сервиса параллельно — TCP-прокси и Flask.

3. **Открыть браузер**:

   Скопируйте ссылку:

   ```
   http://127.0.0.1:5000/?url=http://example.com&embed_ads=1
   ```

   где:

   * `url` — адрес страницы, которую нужно проксировать и очистить
   * `embed_ads=1` — опциональный флаг для встраивания кастомного баннера

## Настройка браузера

* Откройте настройки сети и выставьте HTTP-прокси: `127.0.0.1:8080`.
* **Важно:** для HTTPS оставьте поле пустым и **не** ставьте флажок "использовать тот же прокси для HTTPS".
* Все HTTP-запросы браузер будет отдавать через низкоуровневый прокси, а веб-прокси на Flask будет использоваться для HTML-фильтрации.

##  Тестирование

Запустите юнит-тесты:

```bash
pytest tests/test_dump_and_hosts.py
pytest tests/test_factorial.py
pytest tests/test_html_utils.py
pytest tests/test_request_utils.py
pytest tests/test_web_proxy.py
```

Они покрывают:

* Проверку HTTP и HTTPS через прокси
* Разбор и модификацию HTTP-запросов (`GET`, `CONNECT`)
* Удаление рекламных элементов из HTML
* Блокировку рекламных доменов

## Конфигурирование

* **`ad_hosts.txt`** — каждый домен с новой строки, комментировать `#`.
* **`Server/banners.py`** — редактируйте баннеры и правила выбора.


Автор: Андрей Султанов
