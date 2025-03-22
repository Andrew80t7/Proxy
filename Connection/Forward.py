import socket


class Forward:
    """
    Класс для установки прямого соединения с сервером.

    """

    def __init__(self):
        """Инициализирует новый TCP-сокет."""
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host: str, port: int):
        """
        Устанавливает соединение с сервером.

        """
        try:
            self.forward.connect((host, port))
            return self.forward
        except TimeoutError:
            return None