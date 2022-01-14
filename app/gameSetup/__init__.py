from flask import Blueprint

gameSetup = Blueprint('gameSetup', __name__)

from . import views
