import sys
import os
import glob
import time
import tempfile

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import Server.ProxyServer as ps


def test_is_ad_host(tmp_path, monkeypatch):
    # Поменяем AD_HOSTS_1
    ps.AD_HOSTS_1.clear()
    ps.AD_HOSTS_1.add("ads.test.com")
    assert ps.is_ad_host("ads.test.com")
    assert ps.is_ad_host("sub.ads.test.com")
    assert not ps.is_ad_host("notads.test.com")


def test_save_dump_creates_file(tmp_path, monkeypatch):
    # Направим DUMP_DIR во временную папку
    monkeypatch.setattr(ps, 'DUMP_DIR', str(tmp_path))
    data1 = b"hello"
    ps.save_dump(data1, "req")
    # немного подождём, чтобы вторая метка времени стала другой
    time.sleep(0.01)
    data2 = b"world"
    ps.save_dump(data2, "resp")

    # ищем оба типа файлов
    pattern = str(tmp_path / "*_*.dump")
    files = glob.glob(pattern)
    assert len(files) >= 2

    # проверяем содержимое одного из дампов
    content = open(files[0], "rb").read()
    assert b"Timestamp:" in content
    assert b"Direction:" in content
    assert b"hello" in content or b"world" in content
