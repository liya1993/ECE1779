import PIL
import  os
from PIL import Image
from app import  webapp
def create_thumbnail(image):
    base_width = 80
    img = Image.open(os.path.join(webapp.config['UPLOAD_FOLDER'], image))
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(os.path.join(webapp.config['THUMBNAIL_FOLDER'], image))

# @webapp.route('/user/thumbnails',methods='GET')