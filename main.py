import sys
import time
from Server.ProxyServer import ProxyServer
from Logs.logger import get_logger

logger = get_logger()

HOST = 'localhost'
PORT = 8080

global server

if __name__ == '__main__':
    try:
        server = ProxyServer(HOST, PORT)
        logger.info(f"Сервер запущен на {HOST}:{PORT}")
        server.main_loop()


    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, остановка сервера")
        if server:
            server.shutdown()

    except Exception as e:
        logger.error(f"Ошибка при работе сервера: {e}")
        if server:
            server.shutdown()
        sys.exit(1)
    finally:
        time.sleep(1)
