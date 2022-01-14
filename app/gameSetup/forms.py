from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from ..models import GameDetails


class GameSetupForm(FlaskForm):
    game_title = StringField('Game Title', validators=[DataRequired()])
    match_id= IntegerField ('Unique Match ID', validators=[DataRequired()])
    game_status=StringField('Active/Inactive', validators=[DataRequired()]) 
    squad_link=StringField('Enter the link for squad', validators=[DataRequired()])  
    game_start_time = StringField('Game Start Time in EST [year,month,day,hour,minute]') 
    submit = SubmitField('Setup')

############# FORM TO DISPLAY ACTIVE GAMES IN THE DATABASE AND COLLECT USER INPUT
class ActiveGamesForm(FlaskForm): 
    
    game_selection = SelectField(u'Select a game: ', coerce=int)
    submit = SubmitField('Next')  

######## ------------------------------------------------------####  

############# FORM TO DISPLAY ACTIVE GAMES IN THE DATABASE AND COLLECT USER INPUT
class DeactivateGameForm(FlaskForm): 
    
    game_selection = SelectField(u'Select a game: ', coerce=int)
    submit = SubmitField('Deactivate')  

######## ------------------------------------------------------#### 

class AddScoreCardForm(FlaskForm):  
    score_card_link = StringField('Enter the link for score card', validators=[DataRequired()])   
    points_per_run = FloatField ('Enter the weight for each run', validators=[DataRequired()])  
    points_per_wicket = FloatField ('Enter the weight for each wicket', validators=[DataRequired()])   
    submit = SubmitField('Setup') 

######## ------------------------------------------------------####  
class UpdateGameDetailsForm(FlaskForm): 
    game_selection = SelectField(u'Select a game: ', coerce=int) 
    game_start_time = StringField('Game Start Time in EST [year,month,day,hour,minute]') 
    updated_squad_link = StringField('Enter the updated link for squad/Playing Xi') 
    
    submit = SubmitField('Setup') 