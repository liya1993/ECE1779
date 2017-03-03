from flask import  Blueprint
from flask import Flask

# main = Blueprint(__name__)
webapp = Flask(__name__)

from . import views
from . import errors
