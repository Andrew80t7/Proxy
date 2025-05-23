import sys
import threading
import time
import urllib.parse
import webbrowser
import requests
from flask import Flask, request, Response
from Logs.logger import get_logger
from Server.ProxyServer import ProxyServer, modify_html
from bs4 import BeautifulSoup
from Server.banners import change_banners, BANNERS

# Инициализация логгера
logger = get_logger()

app = Flask(__name__, static_folder="static", static_url_path="/static")

# Настройки прокси
PROXY = {"http": "http://127.0.0.1:8080", "https": None}


def rewrite_links(html: str, base_url: str, embed_ads: bool, flag: int) -> str:
    """
    Переписывает ссылки в HTML, чтобы они вели обратно на прокси-сервер.
    Также вставляет рекламный баннер в начало <body>.

    :param html: HTML-код страницы
    :param base_url: Исходный URL страницы
    :param embed_ads: Вставлять ли баннеры
    :param flag: Флаг, определяющий тип баннера
    :return: Изменённый HTML
    """
    soup = BeautifulSoup(html, "html.parser")

    # Генерация и вставка баннера
    banner_html = change_banners(BANNERS, flag)
    if banner_html:
        banner_fragment = BeautifulSoup(banner_html, "html.parser")
        if body := soup.find("body"):
            body.insert(0, banner_fragment)

    # Переписываем ссылки и ресурсы
    for tag in soup.find_all(["a", "link", "script", "img", "iframe"]):
        attribute = (
            "href"
            if tag.has_attr("href")
            else ("src" if tag.has_attr("src") else None)
        )
        if not attribute:
            continue

        orig = tag[attribute]
        abs_url = urllib.parse.urljoin(base_url, orig)
        query = {"url": abs_url}
        if embed_ads:
            query["embed_ads"] = "1"
        enc = urllib.parse.urlencode(query, quote_via=urllib.parse.quote_plus)
        tag[attribute] = f"/?{enc}"

    return str(soup)


@app.route("/", methods=["GET"])
def proxy():
    """
    Получает URL, делает запрос, очищает HTML от нежелательных элементов,
    переписывает ссылки и возвращает пользователю.
    """
    url = request.args.get("url")

    try:
        flag = int(request.args.get("flag", "2"))  # флаг баннеров
    except ValueError:
        flag = 1

    # Запрос к целевому ресурсу
    resp = requests.get(url, headers={})
    content_type = resp.headers.get("Content-Type", "")

    if "text/html" in content_type.lower():
        # Если HTML — очищаем от рекламы и переписываем ссылки
        cleaned_html_bytes, blocked_elements = modify_html(resp.content)
        cleaned_html = cleaned_html_bytes.decode("utf-8", errors="ignore")

        final_html = rewrite_links(
            cleaned_html, url, embed_ads=True, flag=flag
        )
        return Response(
            final_html, headers={"Content-Type": "text/html; charset=utf-8"}
        )

    # Если не HTML — возвращаем как есть
    return Response(resp.content, headers={"Content-Type": content_type})


def run_proxy():
    """
    Запускает HTTP-прокси-сервер на порту 8080.
    """
    srv = ProxyServer("127.0.0.1", 8080)
    try:
        srv.main_loop()
    finally:
        srv.shutdown()


def run_web():
    """
    Запускает веб-сервер на порту 5000.
    """
    app.run(port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":

    # прокси и веб-сервер в отдельных потоках
    proxy_thread = threading.Thread(target=run_proxy, daemon=True)
    web_thread = threading.Thread(target=run_web, daemon=True)

    proxy_thread.start()
    web_thread.start()

    time.sleep(1)  # ждём пока сервера поднимутся

    # Стартовая страница

    start_url = (
        "http://www.realto.ru/journal/articles/interesnye-fakty-o-kazino/"
    )
    webbrowser.open(
        f"http://127.0.0.1:5000/?url={urllib.parse.quote_plus(start_url)}"
        f"&embed_ads=1"
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Завершение работы")
        sys.exit(0)
