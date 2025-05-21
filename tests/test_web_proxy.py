import urllib.parse
import pytest
from flask import Response
from bs4 import BeautifulSoup

import web_proxy
from web_proxy import app, rewrite_links


class DummyResp:
    def __init__(self, content: bytes, content_type: str):
        self.content = content
        self.headers = {'Content-Type': content_type}


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_rewrite_links_with_banner_and_resources():
    html = """
    <html><head></head><body>
      <script src="/js/app.js"></script>
      <img src="img.png"/>
    </body></html>
    """
    out = rewrite_links(html, "http://site/", embed_ads=True, flag=1)
    soup = BeautifulSoup(out, "html.parser")
    # проверим, что баннер вставлен первым элементом в body
    body_children = list(soup.body.children)
    first_div = next((c for c in body_children if c.name == "div"), None)
    assert first_div is not None
    # Проверяем, что ресурсы переписаны через прокси
    scripts = soup.find_all("script")
    imgs = soup.find_all("img")
    assert all(src.get("src", "").startswith("/?url=") for src in imgs)
    assert all(scr.get("src", "").startswith("/?url=") for scr in scripts)


@pytest.mark.parametrize("url,ctype,expected_snippet", [
    ("http://foo.com", "text/html; charset=utf-8", True),
    ("http://foo.com", "TEXT/HTML", True),
    ("http://foo.com", "application/json", False),
])
def test_proxy_route_content_type(monkeypatch, client, url, ctype, expected_snippet):
    dummy_html = b"<html><body>HELLO</body></html>"

    # 1) подменим requests.get
    def fake_get(target, headers):
        return DummyResp(dummy_html, ctype)

    monkeypatch.setattr(web_proxy.requests, "get", fake_get)

    # 2) подменим modify_html, чтобы вернуть оригинал без блокировок
    def fake_modify(html_bytes):
        return html_bytes, []

    monkeypatch.setattr(web_proxy, "modify_html", fake_modify)

    # вызов
    resp: Response = client.get(f"/?url={urllib.parse.quote_plus(url)}&flag=2")
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    if expected_snippet:
        # после modify_html берётся rewrite_links с embed_ads=True,
        # значит в HTML должна быть вставка баннера
        assert "telegram-banner" in data or "white_house_banner" in data
    else:
        # для не-html просто стримим оригинальный контент
        assert data == dummy_html.decode()


