import sys
import os

# чтобы найти пакет Server
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from Server.ProxyServer import modify_html

HTML_SAMPLE = b"""
<html>
<head><title>Test</title></head>
<body>
  <div class="ad-container">AD</div>
  <img src="http://ads.example.com/banner.jpg" width="300" height="250"/>
  <p>Keep me</p>
</body>
</html>
"""


def test_modify_html_removes_ad_div_and_img():
    cleaned_bytes, blocked = modify_html(HTML_SAMPLE)
    cleaned = cleaned_bytes.decode('utf-8')
    # заблокированы оба рекламных элемента
    assert any(b['selector'] == '.ad-container' for b in blocked)
    assert any('ads.example.com' in b['src'] for b in blocked)
    # в итоговом HTML их нет
    assert 'ad-container' not in cleaned
    assert 'ads.example.com' not in cleaned


def test_modify_html_injects_style():
    cleaned_bytes, _ = modify_html(HTML_SAMPLE)
    cleaned = cleaned_bytes.decode('utf-8')
    # в результате должен быть наш <style>
    assert '.telegram-banner' in cleaned
