from flask import Blueprint

fantasyContest = Blueprint('fantasyContest', __name__)

from . import views
