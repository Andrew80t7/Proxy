import socket
from Logs.logger import get_logger

logger = get_logger()


class Forward:
    """
    Класс для установки прямого соединения с сервером
    """

    def __init__(self):
        self.forward = None
        self.timeout = 5  # Таймаут для соединения в секундах

    def start(self, host: str, port: int) -> None:
        """
        Устанавливает соединение с целевым сервером.

        Args:
            host (str): Хост целевого сервера
            port (int): Порт целевого сервера

        Returns:
            socket.socket: Сокет соединения или None в случае ошибки
        """
        try:
            logger.debug(f"Попытка подключения к {host}:{port}")
            self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.forward.settimeout(self.timeout)
            # Включаем TCP keepalive
            self.forward.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Устанавливаем TCP_NODELAY для уменьшения задержек
            self.forward.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            # Пробуем подключиться
            self.forward.connect((host, port))
            logger.info(f"Успешное подключение к {host}:{port}")
            return self.forward

        except socket.timeout:
            logger.error(f"Таймаут при подключении к {host}:{port}")
            self.cleanup()
            return None
        except ConnectionRefusedError:
            logger.error(f"Соединение отклонено сервером {host}:{port}")
            self.cleanup()
            return None
        except Exception as e:
            logger.error(f"Ошибка при подключении к {host}:{port}: {e}")
            self.cleanup()
            return None

    def cleanup(self):
        """
        Очищает ресурсы соединения
        """
        if self.forward:
            try:
                self.forward.close()
            except OSError:
                pass
            self.forward = None
