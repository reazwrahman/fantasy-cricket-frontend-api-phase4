from flask import Blueprint

squadSelection = Blueprint('squadSelection', __name__)

from . import views
