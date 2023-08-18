from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from multipart import MultipartParser, copy_file
from subprocess import run as process_run, PIPE
import gzip
import os

class MyHTTPHandler(BaseHTTPRequestHandler):
    HTTP_DT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

    def write_data(self, bytes_data):
        self.send_header('Content-Encoding', 'gzip')
        return_data = gzip.compress(bytes_data)
        self.send_header('Content-Length', len(return_data))
        self.end_headers()
        self.wfile.write(return_data)

    def handle_post_request(self):
        self.log_message(f"Reading POST request from {self.client_address}")
        content_length = int(self.headers['Content-Length'])
        content_boundary = self.headers['Content-Type'].split('=')[1]

        self.data = MultipartParser(self.rfile, content_boundary, content_length)
        image_data = self.execute_cgi_process(self.data.get('image_data'))
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        return image_data

    def execute_cgi_process(self, image_entry):
        image_buffer = BytesIO()
        size = copy_file(image_entry.file, image_buffer)
        cgi_env = {
            **os.environ,
            'SERVER_SOFTWARE': 'PyPy/3.10.12',
            'SERVER_NAME': 'raspberrypi',
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'SERVER_PORT': str(PORT),
            'REQUEST_METHOD': 'POST',
            'QUERY_STRING': '',
            'SCRIPT_NAME': 'cgi_application.py',
            'REMOTE_HOST': self.client_address[0],
            'CONTENT_TYPE': 'image/png',
            'CONTENT_LENGTH': str(size)
        }
        p_handle = process_run(['pypy', 'cgi_application.py'], input=image_buffer.getvalue(), capture_output=True, env=cgi_env)
        if p_handle.stderr:
            print(p_handle.stderr.decode())
        return p_handle.stdout

    def do_POST(self):
        bytes_data = self.handle_post_request()
        self.write_data(bytes_data)
        self.request.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8087

    with ThreadingHTTPServer((HOST, PORT), MyHTTPHandler) as server:
        print(f'Server bound to port {PORT}')
        server.serve_forever()
