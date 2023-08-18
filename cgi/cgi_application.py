import os
from io import BytesIO
from PIL import Image, ImageDraw
from sys import stdin, stdout

if __name__ == '__main__':
    image_data = stdin.buffer.read(int(os.environ['CONTENT_LENGTH']))
    cgi_headers = [
        "SERVER_SOFTWARE", "SERVER_NAME", "GATEWAY_INTERFACE",
        "SERVER_PROTOCOL", "SERVER_PORT", "REQUEST_METHOD",
        "QUERY_STRING", "SCRIPT_NAME", "REMOTE_HOST",
        "CONTENT_TYPE", "CONTENT_LENGTH"]
    header_output = '\n'.join([ os.environ[x] for x in cgi_headers ])
    with Image.open(BytesIO(image_data)) as im:
        resized_image = im.resize((800,800))
        draw = ImageDraw.Draw(resized_image)
        draw.multiline_text((10,10), header_output, fill="black")
        resized_image.save(stdout, 'png')