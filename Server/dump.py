import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
if not os.path.exists(DUMP_DIR):
    os.makedirs(DUMP_DIR)


class DumpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DUMP_DIR, **kwargs)


def run_dump_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DumpRequestHandler)
    print(f"Dump download server running on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run_dump_server(8000)
