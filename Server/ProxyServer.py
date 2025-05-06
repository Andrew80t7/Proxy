import socket
import time
from datetime import datetime

import select
import errno
import os
from Connection.Forward import Forward
from Logs.logger import get_logger
from typing import Tuple, List
from bs4 import BeautifulSoup

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
os.makedirs(DUMP_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(__file__)
AD_HOSTS_PATH = os.path.join(BASE_DIR, "ad_hosts.txt")

AD_HOSTS_1 = set()

logger = get_logger()


def modify_html(html: bytes) -> Tuple[bytes, List[dict]]:
    """
    удаляет рекламу
    """
    blocked_elements = []
    try:
        soup = BeautifulSoup(html, "html.parser")

        ad_selectors = [
            "div[data-ad-target]",
            ".ad-container",
            ".ad-wrapper",
            'div[id^="adfox_"]',
            'iframe[src*="ads."]',
            'div[class*="banner_ad"]',
            'div[data-type="adsContainer"]',
            'script[src*="adservice"]',
            'img[src*="ads."]',
        ]
        for selector in ad_selectors:
            for tag in soup.select(selector):
                blocked_elements.append(
                    {
                        "selector": selector,
                        "src": tag.get("src", ""),
                        "classes": tag.get("class", ""),
                        "tag": tag.name,
                    }
                )
                tag.decompose()

        style = soup.new_tag("style")
        style.string = """
            .telegram-banner, .casino-banner, .shopping-banner {
                position: fixed !important;
                bottom: 20px !important;
                right: 20px !important;
                z-index: 9999 !important;
                visibility: visible !important;
            }
        """
        if soup.head:
            soup.head.append(style)
        else:
            soup.insert(0, style)

        return str(soup).encode("utf-8"), blocked_elements

    except Exception as e:
        logger.error(f"HTML modification error: {e}")
        return html, blocked_elements


with open("ad_hosts.txt", "r") as f:
    for line in f:
        host = line.strip()
        if host and not host.startswith("#"):
            AD_HOSTS_1.add(host)


def is_ad_host(hst: str) -> bool:
    """Проверка, является ли домен рекламным"""
    return any(hst == d or hst.endswith("." + d) for d in AD_HOSTS_1)


def save_dump(data: bytes, direction: str):
    """
    Сохраняет данные data в файл:

    """

    ts = datetime.now().isoformat(timespec="microseconds").replace(":", "")
    filename = f"{ts}_{direction}.dump"
    path = os.path.join(DUMP_DIR, filename)

    with open(path, "wb") as file:
        header = f"Timestamp: {ts}\nDirection: {direction}\n\n"
        file.write(header.encode("utf-8", errors="ignore"))
        file.write(data)

    logger.debug(f"Dump сохранён: {path}")


# Размер буфера
BUFFER_SIZE = 4096

# Задержка
DELAY = 0.0001

# Таймаут для операций с сокетами
SOCKET_TIMEOUT = 5

# Максимальное количество соединений
MAX_CONNECTIONS = 1000

# логгер
logger = get_logger()


def modify_request(data: bytes) -> bytes:
    try:
        lines = data.split(b"\r\n")
        if not lines:
            return data

        # первая строка: метод, URL, протокол
        first = lines[0].decode("utf-8", errors="ignore").split(" ")
        if len(first) < 3:
            return data
        method, url, proto = first

        if url.startswith("http://") or url.startswith("https://"):
            idx = url.find("/", url.find("://") + 3)
            path = url[idx:] if idx != -1 else "/"
            lines[0] = b" ".join(
                [method.encode(), path.encode(), proto.encode()]
            )
        return b"\r\n".join(lines)
    except UnicodeError:
        return data


def parse_request(data: bytes):
    """Извлекает метод, хост и порт"""

    lines = data.split(b"\r\n")
    if not lines:
        return None, None, None

    first_line = lines[0].decode("utf-8", errors="ignore")
    parts = first_line.split(" ")
    if len(parts) < 2:
        return None, None, None

    method = parts[0]

    if method == "CONNECT":
        host_port = parts[1].split(":")
        HOST = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 443
        return "CONNECT", HOST, port
    else:
        # Обработка заголовков
        for tag_line in lines[1:]:
            try:
                # Декодируем каждую строку заголовка
                line_str = tag_line.decode("utf-8", errors="ignore")
                if line_str.lower().startswith("host:"):
                    host_port = line_str.split(":", 1)[1].strip()
                    if ":" in host_port:
                        HOST, port = host_port.split(":")
                        port = int(port)
                    else:
                        HOST = host_port
                        port = 80
                    return method, HOST, port
            except Exception as e:
                print(f"Ошибка при обработке заголовка: {e}")
        return None, None, None


class ProxyServer:
    """
    Основной класс сервера

    """

    def __init__(self, HOST: str, PORT: int):
        """
        Инициализирует прокси-сервер.

        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(SOCKET_TIMEOUT)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(200)
        self.input_list = [self.server]
        self.channel = {}
        self.running = True
        self.last_cleanup = time.time()
        logger.info(f"Прокси-сервер инициализирован на {HOST}:{PORT}")

    def _cleanup_inactive_connections(self):
        """
        Очищает неактивные соединения
        """

        current_time = time.time()
        if current_time - self.last_cleanup < 60:  # Проверяем каждую минуту
            return

        try:

            valid_sockets = []

            for s in self.input_list:
                try:
                    if s.fileno() != -1:
                        valid_sockets.append(s)
                    else:
                        if s in self.channel:
                            self._cleanup_peer_connection(s)
                except OSError:
                    if s in self.channel:
                        self._cleanup_peer_connection(s)

            self.input_list = valid_sockets
            self.last_cleanup = current_time
            logger.info(f"Очищено {len(self.input_list)} активных соединений")
        except OSError as e:
            logger.error(f"Ошибка при очистке соединений: {e}")

    def main_loop(self):
        """
        Основной цикл обработки событий сервера.
        """
        logger.info("Сервер запущен и ожидает подключений")

        while self.running:
            try:
                time.sleep(DELAY)
                self._cleanup_inactive_connections()

                if not self.input_list:
                    logger.warning("Нет активных сокетов, завершение работы")
                    break

                # Используем таймаут для select, чтобы не блокировать навсегда
                input_ready, _, _ = select.select(self.input_list, [], [], 0.1)
                for s in input_ready:
                    if s == self.server:
                        self.on_accept()
                    else:
                        self.on_recv(s)
            except select.error as e:
                if e.args[0] == errno.EBADF:
                    logger.warning(
                        "Обнаружен невалидный файловый дескриптор, очистка сокетов"
                    )
                    self._cleanup_inactive_connections()
                else:
                    logger.error(f"Ошибка select: {e}")
            except Exception as e:
                logger.error(f"Ошибка в главном цикле: {e}")
                self._cleanup_inactive_connections()

    def on_accept(self):
        """
        Обрабатывает новое клиентское подключение.
        """
        try:
            clientsock, clientaddr = self.server.accept()
            clientsock.settimeout(SOCKET_TIMEOUT)
            # Устанавливаем TCP_NODELAY для уменьшения задержек
            clientsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            logger.info(f"Новое подключение от {clientaddr}")
            self.input_list.append(clientsock)
            self.channel[clientsock] = {
                "peer": None,
                "parse": True,
                "type": None,
            }
        except socket.timeout:
            # Игнорируем таймауты при принятии соединений
            pass
        except OSError as e:
            logger.error(f"Ошибка при принятии соединения: {e}")

    def on_recv(self, s: socket.socket):
        """
        Обрабатывает данные от клиента или сервера.
        """
        try:
            # Проверяем, что сокет всё ещё валиден
            if s.fileno() == -1:
                logger.warning("Получен запрос от невалидного сокета")
                self._cleanup_inactive_connections()
                return

            data = s.recv(BUFFER_SIZE)
            if not data:
                self.on_close(s)
                return

            # Сохраняем запросы в дампс

            save_dump(data, "request")

            if s in self.channel and self.channel[s]["parse"]:
                method, HOST, port = parse_request(data)

                if method == "CONNECT" and HOST and is_ad_host(HOST):
                    logger.info(f"BLOCKING CONNECT to ad host: {HOST}")
                    s.send(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                    return

                if HOST and is_ad_host(HOST):
                    # Увеличиваем счётчик заблокированных запросов
                    self.channel[s].setdefault("blocked_count", 0)
                    self.channel[s]["blocked_count"] += 1

                    logger.info(
                        f"Блокировка запроса к рекламному домену: {HOST} (total blocked: {
                            self.channel[s]['blocked_count']})")
                    if method == "CONNECT":
                        # Блокируем HTTPS CONNECT
                        s.send(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                    else:
                        # Блокируем HTTP-запрос
                        resp = b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n"
                        s.send(resp)
                        save_dump(resp, "blocked")
                    return

                if method and HOST and port:
                    logger.debug(f"Запрос: {method} {HOST}:{port}")
                    forward = Forward().start(HOST, port)
                    if forward:
                        self._setup_forward_connection(
                            s, forward, method, data
                        )
                    else:
                        self._handle_connection_error(HOST, port, s)
                else:
                    self._handle_invalid_request(s)

            else:
                # Далее передаем данные (HTTP или HTTPS-туннель)
                self._forward_data(s, data)

        except socket.timeout:
            # Игнорируем таймауты при чтении данных
            pass
        except ConnectionAbortedError:
            logger.warning(f"Соединение разорвано: {s.getpeername()}")
            self.on_close(s)
        except OSError as e:
            logger.error(f"Ошибка при получении данных: {e}")
            self.on_close(s)

    def _setup_forward_connection(
        self,
        s: socket.socket,
        forward: socket.socket,
        method: str,
        data: bytes,
    ):
        """
        Настраивает соединение с целевым сервером.
        """
        try:
            self.channel[s]["peer"] = forward
            self.channel[forward] = {"peer": s, "parse": False, "type": method}

            if method == "CONNECT":
                self._handle_https_connection(s)
            else:
                self._handle_http_connection(s, forward, data)
        except OSError as e:
            logger.error(f"Ошибка при настройке соединения: {e}")
            self.on_close(s)

    def _handle_https_connection(self, s: socket.socket):
        """
        Обрабатывает HTTPS-соединение
        """
        try:
            logger.debug("Установка HTTPS-соединения")
            # Отправляем успешный ответ клиенту
            s.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            # Настраиваем соединение
            self.channel[s]["type"] = "CONNECT"
            self.channel[s]["parse"] = False

            # Добавляем peer в список для мониторинга
            peer = self.channel[s]["peer"]
            if peer and peer not in self.input_list:
                self.input_list.append(peer)
                logger.debug("Peer добавлен в список мониторинга")

            logger.info("HTTPS-соединение установлено")
        except OSError as e:
            logger.error(f"Ошибка при установке HTTPS-соединения: {e}")
            self.on_close(s)

    def _handle_http_connection(
        self, s: socket.socket, forward: socket.socket, data: bytes
    ):
        """
        Обрабатывает HTTP-соединение.
        """
        try:
            logger.debug("Обработка HTTP-соединения")
            new_data = modify_request(data)
            forward.send(new_data)
            self.channel[s]["type"] = "HTTP"
            self.channel[s]["parse"] = False
            self.input_list.append(forward)
        except OSError as e:
            logger.error(f"Ошибка при обработке HTTP-соединения: {e}")
            self.on_close(s)

    def _handle_connection_error(self, HOST: str, PORT: int, s: socket.socket):
        """
        Обрабатывает ошибку подключения.
        """
        logger.error(f"Не удалось подключиться к {HOST}:{PORT}")
        self.on_close(s)

    def _handle_invalid_request(self, s: socket.socket):
        """
        Обрабатывает некорректный запрос.
        """
        logger.warning("Получен некорректный запрос")
        self.on_close(s)

    def _forward_data(self, s: socket.socket, data: bytes):
        peer = self.channel[s]["peer"]
        # buf = self.channel[s].sedtdefault('resp_bu')
        save_dump(data, "response")

        if self.channel[s].get("type") != "HTTP":
            peer.send(data)
            return

        buf = self.channel[s].setdefault("resp_buf", b"") + data
        if b"\r\n\r\n" not in buf:
            self.channel[s]["resp_buf"] = buf
            return

        headers, body = buf.split(b"\r\n\r\n", 1)
        headers_str = headers.decode("utf-8", errors="ignore").lower()
        is_html = "content-type:" in headers_str and "text/html" in headers_str

        logger.debug(
            f"is_html={is_html}, headers snippet: {headers_str[:100]!r}"
        )

    def on_close(self, s: socket.socket):
        """
        Закрывает соединение и освобождает ресурсы.

        """
        try:
            if s in self.input_list:
                try:
                    client_addr = s.getpeername()
                    logger.info(f"Закрытие соединения с {client_addr}")
                except OSError:
                    logger.info("Закрытие соединения с неизвестным адресом")

                self.input_list.remove(s)
                if s in self.channel:
                    self._cleanup_peer_connection(s)

                try:
                    s.close()
                except OSError:
                    pass
        except OSError as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")

    def _cleanup_peer_connection(self, s: socket.socket):
        """
        Очищает связанные соединения.
        """
        try:
            if s in self.channel:
                peer = self.channel[s]["peer"]
                if peer and peer in self.input_list:
                    self.input_list.remove(peer)
                    try:
                        peer.close()
                    except OSError:
                        pass
                del self.channel[s]
                if peer in self.channel:
                    del self.channel[peer]
        except OSError as e:
            logger.error(f"Ошибка при очистке соединения: {e}")

    def shutdown(self):
        """
        завершает работу сервера.
        """
        logger.info("Завершение работы сервера")
        self.running = False

        for s in list(self.input_list):
            try:
                if s != self.server:
                    self.on_close(s)
            except OSError:
                pass

        try:
            self.server.close()
        except OSError:
            pass

        logger.info("Сервер остановлен")
