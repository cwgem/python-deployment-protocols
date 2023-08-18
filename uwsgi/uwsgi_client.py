import requests
from io import BytesIO
from PIL import Image

img = Image.new('RGB', (400,400), "white")
img_bytes = BytesIO()
img.save(img_bytes, 'png')

multipart_data = {
    'image_data': ('blank-image.png', img_bytes.getbuffer(), 'image/png')
}

r = requests.post('http://localhost:9898/', files=multipart_data)
with open('image-resized.png', 'wb') as resized_image_fp:
    resized_image_fp.write(r.content)