import os

from PIL import Image
from flask import current_app


def upload_post_image(image, blog_id):
    new_filename = image.filename
    file_extension = new_filename.split(".")[-1]
    new_filename = str(blog_id) + "_post_image." + str(file_extension)

    filepath = os.path.join(current_app.root_path, r"static/post/post-images", new_filename)

    image = Image.open(image)
    image.save(filepath)

    return new_filename
