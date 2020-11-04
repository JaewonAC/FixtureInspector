import os
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

os.system('python3 pixel.py ceremony 0.3')

from app import routes