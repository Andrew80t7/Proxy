import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from Server.ProxyServer import parse_request, modify_request


def test_parse_request_http_standard():
    raw = b"GET http://foo.bar/baz HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
    method, host, port = parse_request(raw)
    assert method == "GET"
    assert host == "foo.bar"
    assert port == 80


def test_parse_request_connect():
    raw = b"CONNECT secure.example:443 HTTP/1.1\r\nHost: secure.example:443\r\n\r\n"
    method, host, port = parse_request(raw)
    assert method == "CONNECT"
    assert host == "secure.example"
    assert port == 443


def test_parse_request_missing_host_header():
    raw = b"GET /nohost HTTP/1.1\r\nUser-Agent: tests\r\n\r\n"
    method, host, port = parse_request(raw)
    assert method is None and host is None and port is None


def test_modify_request_rewrites_absolute_url():
    req = b"GET http://foo.bar/path HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
    out = modify_request(req)
    assert b"GET /path HTTP/1.1" in out


def test_modify_request_leaves_relative():
    req = b"GET /already HTTP/1.1\r\nHost: foo.bar\r\n\r\n"
    out = modify_request(req)
    assert b"GET /already HTTP/1.1" in out


def test_modify_request_malformed_bytes():
    broken = b"\xff\xfe\x00"
    out = modify_request(broken)
    # при ошибке возвращается оригинал
    assert out == broken
