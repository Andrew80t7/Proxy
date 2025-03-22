import sys
from Server.ProxyServer import TheServer


HOST = 'localhost'
PORT = 8080


if __name__ == '__main__':

    server = TheServer(HOST, PORT)

    print(f"Сервер запущен на {HOST}:{PORT}")
    try:
        server.main_loop()

    except KeyboardInterrupt:
        print("Остановка сервера")
        sys.exit(1)
