from fastcgi import FcgiHandler
from multipart import MultipartParser
from PIL import Image, ImageDraw
from socketserver import ThreadingTCPServer

HEADER_ENCODING = 'iso-8859-1'

class MyFcgiHandler(FcgiHandler):
    def handle(self):
        content_length = int(self.environ['CONTENT_LENGTH'])
        content_boundary = self.environ['CONTENT_TYPE'].split('=')[1]
        self.data = MultipartParser(self['stdin'], content_boundary, content_length)

        image_entry = self.data.get('image_data')
        self['stdout'].write(b'Content-Type: image/png\r\n')
        header_output = '\n'.join([ f'{k}: {v}' for k, v in self.environ.items() ])

        with Image.open(image_entry.file) as im:
            resized_image = im.resize((800,800))
            draw = ImageDraw.Draw(resized_image)
            draw.multiline_text((10,10), header_output, fill="black")
            self['stdout'].write(f'Content-Length: {resized_image.size}\r\n\r\n'.encode(HEADER_ENCODING))
            resized_image.save(self['stdout'], 'png')

        image_entry.file.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8087

    with ThreadingTCPServer((HOST, PORT), MyFcgiHandler) as server:
        print(f'Server bound to port {PORT}')
        server.serve_forever()