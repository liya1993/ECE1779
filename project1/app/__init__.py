from flask import Flask
from flask import flash

# main = Blueprint(__name__)
webapp = Flask(__name__)
webapp.secret_key = 'some_secret'

from app import errors
from app import views
from app import forms