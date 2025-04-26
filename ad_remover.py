from mitmproxy import http
from bs4 import BeautifulSoup

ad_hosts = ["ads.realto.ru", "doubleclick.net", "yastatic.net"]


def response(flow: http.HTTPFlow):
    if "text/html" in flow.response.headers.get("content-type", ""):
        html = flow.response.get_text()
        soup = BeautifulSoup(html, "html.parser")

        # удаляем iframe и скрипты с внешних ad_hosts
        for tag in soup.find_all(["script", "iframe"]):
            src = tag.get("src", "")
            if any(ad in src for ad in ad_hosts):
                tag.decompose()

        # убираем встроенные блоки по атрибутам
        for grp in soup.select('div.left-menu__group'):
            if grp.find('a', href="/reklama/"):
                grp.decompose()

        flow.response.set_text(str(soup))

# Встраиватель рекламы