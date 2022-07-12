from flask import Blueprint
from flask_cors import CORS, cross_origin

bp = Blueprint('api', __name__)

from api import api
