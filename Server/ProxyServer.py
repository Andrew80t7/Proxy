import socket
import time
import select
import errno
from Connection.Forward import Forward
from Logs.logger import get_logger
import re
import os
import gzip
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
os.makedirs(DUMP_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(__file__)
AD_HOSTS_PATH = os.path.join(BASE_DIR, 'ad_hosts.txt')

# BASE_DIR = os.path.dirname(__file__)
# HTML_PATH = os.path.join(BASE_DIR, 'html_content.html')

HTML_DUMP_DIR = os.path.join(os.path.dirname(__file__), "html_dumps")
os.makedirs(HTML_DUMP_DIR, exist_ok=True)

AD_HOSTS_1 = set()

logger = get_logger()


def decode_chunked(body: bytes) -> bytes:
    """
    Простая реализация декодирования Transfer-Encoding: chunked
    """
    decoded = b''
    i = 0
    while True:
        # читаем размер следующего чанка (шестнадцатерично)
        pos = body.find(b'\r\n', i)
        if pos == -1:
            break
        length = int(body[i:pos].split(b';')[0], 16)
        if length == 0:
            break
        start = pos + 2
        decoded += body[start:start + length]
        i = start + length + 2  # пропускаем \r\n после данных
    return decoded


def modify_html(html: bytes) -> bytes:
    """
    Удаляет из HTML теги, связанные с рекламными доменами:
    <a>, <script>, <iframe>, <img> и т.д.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup.find_all(attrs={'data-widget-id': True}):
            tag.decompose()

        for tag in soup.find_all('div', attrs={'data-type': 'container'}):
            tag.decompose()

        for tag in soup.find_all('div', attrs={'data-type': 'adsContainer'}):
            tag.decompose()
        for tag in soup.find_all('div', attrs={'data-type': 'mainContainer'}):
            tag.decompose()

        for ad in soup.select('div[data-name="adWrapper"]'):
            ad.decompose()

        for ad in soup.find_all('div', attrs={'data-ad-id': True}):
            ad.decompose()

        for ad in soup.select('div[data-name="adaptiveConstructorAd"]'):
            ad.decompose()

        # 1) Удаляем все ссылки <a> на рекламные домены
        for a in soup.find_all('a', href=True):
            host = urlparse(a['href']).netloc
            if is_ad_host(host):
                a.decompose()

        # Удаляем скрипты <script> с src на рекламные домены
        for tag in soup.find_all('script', src=True):
            host = urlparse(tag['src']).netloc
            if is_ad_host(host):
                tag.decompose()

        # То же для <iframe>
        for tag in soup.find_all('iframe', src=True):
            host = urlparse(tag['src']).netloc
            if is_ad_host(host):
                tag.decompose()

        # И для изображений <img>
        for img in soup.find_all('img', src=True):
            host = urlparse(img['src']).netloc
            if is_ad_host(host):
                img.decompose()

        for grp in soup.select('div.left-menu__group'):
            if grp.find('a.left-menu__group__link', href="/reklama/"):
                grp.decompose()

        for group in soup.find_all('div', class_='left-menu__group'):
            link = group.find('a', class_='left-menu__group__link', href=True)
            if link and link.get_text(strip=True) == 'Реклама':
                group.decompose()

        # Удаляем внешние скрипты с рекламных доменов
        for tag in soup.find_all(['script', 'iframe']):
            src = tag.get('src', '')
            if any(ad_domain in src for ad_domain in
                   ['doubleclick.net', 'googlesyndication.com', 'adfox.ru', 'yandex.ru/ads']):
                tag.decompose()  # Удаляем известные рекламные блоки по class/id

        for selector in ['.yandex_rtb_R-A-1654496-5', '#adfox_mp_0_108530041342_2']:
            for tag in soup.select(selector):
                tag.decompose()

        return str(soup).encode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка при модификации HTML: {e}")
    return html


with open('ad_hosts.txt', 'r') as f:
    for line in f:
        host = line.strip()
        if host and not host.startswith('#'):
            AD_HOSTS_1.add(host)


def is_ad_host(hst: str) -> bool:
    """Проверка, является ли домен рекламным """
    return any(hst == d or hst.endswith('.' + d) for d in AD_HOSTS_1)


def save_dump(data: bytes, direction: str):
    """
    Сохраняет байты data в файл с меткой direction.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{direction}_{ts}.dump"
    path = os.path.join(DUMP_DIR, filename)
    with open(path, 'wb') as f:
        f.write(data)

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
        lines = data.split(b'\r\n')
        if not lines:
            return data

        # первая строка: метод, URL, протокол
        first = lines[0].decode('utf-8', errors='ignore').split(' ')
        if len(first) < 3:
            return data
        method, url, proto = first

        # только если URL абсолютный — отрезаем хост
        if url.startswith("http://") or url.startswith("https://"):
            idx = url.find('/', url.find('://') + 3)
            path = url[idx:] if idx != -1 else '/'
            lines[0] = b' '.join([method.encode(), path.encode(), proto.encode()])
        return b'\r\n'.join(lines)
    except UnicodeError:
        return data


def parse_request(data: bytes):
    '''Извлекает метод, хост и порт'''

    # Разделяем данные на строки по \r\n
    lines = data.split(b'\r\n')
    if not lines:
        return None, None, None

    # Декодируем первую строку запроса
    first_line = lines[0].decode('utf-8', errors='ignore')
    parts = first_line.split(' ')
    if len(parts) < 2:
        return None, None, None

    method = parts[0]

    # Обработка метода CONNECT
    if method == 'CONNECT':
        host_port = parts[1].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 443
        return 'CONNECT', host, port
    else:
        # Обработка заголовков
        for line in lines[1:]:
            try:
                # Декодируем каждую строку заголовка
                line_str = line.decode('utf-8', errors='ignore')
                if line_str.lower().startswith('host:'):
                    host_port = line_str.split(':', 1)[1].strip()
                    if ':' in host_port:
                        host, port = host_port.split(':')
                        port = int(port)
                    else:
                        host = host_port
                        port = 80
                    return method, host, port
            except Exception as e:
                print(f"Ошибка при обработке заголовка: {e}")
        return None, None, None


class ProxyServer:
    """
    Основной класс сервера

    """

    def __init__(self, host: str, port: int):
        """
        Инициализирует прокси-сервер.

        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(SOCKET_TIMEOUT)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server.bind((host, port))
        self.server.listen(200)
        self.input_list = [self.server]
        self.channel = {}
        self.running = True
        self.last_cleanup = time.time()
        logger.info(f"Прокси-сервер инициализирован на {host}:{port}")

    def _cleanup_inactive_connections(self):
        """
        Очищает неактивные соединения
        """
        current_time = time.time()
        if current_time - self.last_cleanup < 60:  # Проверяем каждую минуту
            return

        try:
            # Очищаем невалидные сокеты
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
        """Основной цикл обработки событий сервера."""
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
                    logger.warning("Обнаружен невалидный файловый дескриптор, очистка сокетов")
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
            self.channel[clientsock] = {'peer': None, 'parse': True, 'type': None}
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

            if s in self.channel and self.channel[s]['parse']:
                method, host, port = parse_request(data)

                if method == 'CONNECT' and host and is_ad_host(host):
                    logger.info(f"BLOCKING CONNECT to ad host: {host}")
                    s.send(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                    return

                if host and is_ad_host(host):
                    # Увеличиваем счётчик заблокированных запросов
                    self.channel[s].setdefault('blocked_count', 0)
                    self.channel[s]['blocked_count'] += 1

                    logger.info(
                        f"Блокировка запроса к рекламному домену: {host} (total blocked: {self.channel[s]['blocked_count']})")
                    if method == 'CONNECT':
                        # Блокируем HTTPS CONNECT
                        s.send(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                    else:
                        # Блокируем HTTP-запрос
                        resp = b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n"
                        s.send(resp)
                        save_dump(resp, "blocked")
                    return

                if method and host and port:
                    logger.debug(f"Запрос: {method} {host}:{port}")
                    forward = Forward().start(host, port)
                    if forward:
                        self._setup_forward_connection(s, forward, method, data)
                    else:
                        self._handle_connection_error(host, port, s)
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

    def _setup_forward_connection(self, s: socket.socket, forward: socket.socket, method: str, data: bytes):
        """
        Настраивает соединение с целевым сервером.
        """
        try:
            self.channel[s]['peer'] = forward
            self.channel[forward] = {'peer': s, 'parse': False, 'type': method}

            if method == 'CONNECT':
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
            s.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            # Настраиваем соединение
            self.channel[s]['type'] = 'CONNECT'
            self.channel[s]['parse'] = False

            # Добавляем peer в список для мониторинга
            peer = self.channel[s]['peer']
            if peer and peer not in self.input_list:
                self.input_list.append(peer)
                logger.debug("Peer добавлен в список мониторинга")

            logger.info("HTTPS-соединение установлено")
        except OSError as e:
            logger.error(f"Ошибка при установке HTTPS-соединения: {e}")
            self.on_close(s)

    def _handle_http_connection(self, s: socket.socket, forward: socket.socket, data: bytes):
        """
        Обрабатывает HTTP-соединение.
        """
        try:
            logger.debug("Обработка HTTP-соединения")
            new_data = modify_request(data)
            forward.send(new_data)
            self.channel[s]['type'] = 'HTTP'
            self.channel[s]['parse'] = False
            self.input_list.append(forward)
        except OSError as e:
            logger.error(f"Ошибка при обработке HTTP-соединения: {e}")
            self.on_close(s)

    def _handle_connection_error(self, host: str, port: int, s: socket.socket):
        """
        Обрабатывает ошибку подключения.
        """
        logger.error(f"Не удалось подключиться к {host}:{port}")
        self.on_close(s)

    def _handle_invalid_request(self, s: socket.socket):
        """
        Обрабатывает некорректный запрос.
        """
        logger.warning("Получен некорректный запрос")
        self.on_close(s)

    def _forward_data(self, s: socket.socket, data: bytes):
        """
        Перенаправляет данные от сервера клиенту. Если это HTML,
        декодирует chunked/gzip, вызывает modify_html, вставляет счётчик
        и обновляет заголовок Content-Length.
        """
        peer = self.channel[s]['peer']
        save_dump(data, "response")  # ваш existing dump

        # HTTPS-туннель — просто пересылаем
        if self.channel[s].get('type') != 'HTTP':
            peer.send(data)
            return

        # собираем буфер
        buf = self.channel[s].setdefault('resp_buf', b'') + data
        if b'\r\n\r\n' not in buf:
            self.channel[s]['resp_buf'] = buf
            return

        headers, body = buf.split(b'\r\n\r\n', 1)
        headers_str = headers.decode('utf-8', errors='ignore').lower()
        is_html = 'content-type:' in headers_str and 'text/html' in headers_str

        if is_html:
            # Декодируем chunked и gzip
            if 'transfer-encoding: chunked' in headers_str:
                body = decode_chunked(body)
            if 'content-encoding: gzip' in headers_str:
                body = gzip.decompress(body)

            # Сохраняем декодированный HTML для отладки
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            decoded_path = os.path.join(HTML_DUMP_DIR, f"decoded_{ts}.html")
            try:
                with open(decoded_path, 'wb') as f:
                    f.write(body)
                logger.debug(f"Декодированный HTML сохранён в {decoded_path}")
            except Exception as e:
                logger.error(f"Не удалось сохранить декодированный HTML: {e}")

            # Теперь можно модифицировать рекламо-элементы
            new_body = modify_html(body)

            # … вставка сниппета, пересчёт Content-Length …
            new_headers = re.sub(
                rb'(content-length:\s*)(\d+)',
                lambda m: m.group(1) + str(len(new_body)).encode(),
                headers,
                flags=re.IGNORECASE
            )
            peer.send(new_headers + b'\r\n\r\n' + new_body)
            self.channel[s].pop('resp_buf', None)
            return

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
                peer = self.channel[s]['peer']
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
        Корректно завершает работу сервера.
        """
        logger.info("Завершение работы сервера")
        self.running = False

        # Закрываем все соединения
        for s in list(self.input_list):
            try:
                if s != self.server:
                    self.on_close(s)
            except OSError:
                pass

        # Закрываем серверный сокет
        try:
            self.server.close()
        except OSError:
            pass

        logger.info("Сервер остановлен")
