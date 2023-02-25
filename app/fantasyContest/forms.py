from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms import ValidationError


class ActviveContestantsForm(FlaskForm): 
    
    user_selection = SelectField(u'View the Squad And Fantasy Point Distribution of: ', coerce=str)
    submit = SubmitField('Next')  

######## ------------------------------------------------------####

############# FORM TO DISPLAY ACTIVE GAMES IN THE DATABASE AND COLLECT USER INPUT
class ActiveGamesForm(FlaskForm): 
    
    game_selection = SelectField(u'Select a game: ', coerce=str)
    submit = SubmitField('Next')  

######## ------------------------------------------------------####  
class ViewDetailsForm(FlaskForm):  
    #game_selection = SelectField(u'Select a game: ', coerce=int)
    submit = SubmitField('View Details Point Distribution')  