import os

from PIL import Image, ImageOps
from flask import current_app


def change_profile_image(image_upload, username):
    # filename = img_upload.filename
    storage_filename = str(username) + "_profile_image.jpg"
    print(current_app.root_path)
    filepath = os.path.join(current_app.root_path,
                            r"static/main/images/profile-images", storage_filename)

    img = Image.open(image_upload)

    max_size = max(img.size)
    if max_size > 400:
        max_size = 400
    output_size = (max_size, max_size)

    img = ImageOps.fit(img, output_size, Image.ANTIALIAS)
    img.save(filepath)

    return storage_filename
