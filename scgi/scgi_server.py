from multipart import MultipartParser
from PIL import Image, ImageDraw
from scgi.util import ns_reads, parse_env
from socketserver import ThreadingTCPServer, StreamRequestHandler

HEADER_ENCODING = 'iso-8859-1'

class MyHandler(StreamRequestHandler):
    def parse_body(self):
        header_segment = ns_reads(self.rfile)
        self.headers = parse_env(header_segment)

    def write_headers(self, content_length):
        response_headers = {
            'Content-Type': 'image/png',
            'Content-Length': content_length
        }
        self.wfile.write(b'HTTP/1.1 200 OK\r\n')
        for k,v in response_headers.items():
            self.wfile.write(f'{k}: {v}\r\n'.encode(HEADER_ENCODING))
        self.wfile.write(b'\r\n')

    def send_return(self):
        content_length = int(self.headers['CONTENT_LENGTH'])
        content_boundary = self.headers['CONTENT_TYPE'].split('=')[1]
        self.data = MultipartParser(self.rfile, content_boundary, content_length)

        image_entry = self.data.get('image_data')
        header_output = '\n'.join([ f'{k}: {v}' for k, v in self.headers.items() ])

        with Image.open(image_entry.file) as im:
            resized_image = im.resize((800,800))
            draw = ImageDraw.Draw(resized_image)
            draw.multiline_text((10,10), header_output, fill="black")
            self.write_headers(resized_image.size)
            resized_image.save(self.wfile, 'png')

        image_entry.file.close()

    def handle(self):
        self.headers = {}
        self.content = b''

        self.parse_body()
        self.send_return()
        self.finish()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8087

    with ThreadingTCPServer((HOST, PORT), MyHandler) as server:
        print(f'Server bound to port {PORT}')
        server.serve_forever()
