import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
if not os.path.exists(DUMP_DIR):
    os.makedirs(DUMP_DIR)


class DumpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DUMP_DIR, **kwargs)


def run_dump_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, DumpRequestHandler)
    print(f"Dump download server running on port {port}...")
    httpd.serve_forever()


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return 1 if n <= 1 else n * factorial(n - 1)


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def sum_numbers(numbers: list) -> float:
    return sum(numbers)


if __name__ == "__main__":
    run_dump_server(8000)
