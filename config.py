import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 
    ALLOWED_EXTENSIONS = {'png','jpg', 'jpeg', 'gif'}