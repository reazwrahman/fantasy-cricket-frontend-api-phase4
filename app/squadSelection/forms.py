from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from ..models import GameDetails

############# FORM TO DISPLAY ACTIVE GAMES IN THE DATABASE AND COLLECT USER INPUT
class ActiveGamesForm(FlaskForm): 
    
    game_selection = SelectField(u'Select a game: ', coerce=int)
    submit = SubmitField('Next')  

######## ------------------------------------------------------#### 

## Factory for creating Player Selection Forms ###

class PlayerSelectionFormBase(FlaskForm):
    #submit = wtforms.SubmitField('Submit')  
    pass
    
class PlayerSelectionFormFactory(object): 
    
    def __init__(): 
        pass

    @staticmethod
    def BuildSimpleForm(players_list):
        class PlayerSelectionForm(PlayerSelectionFormBase):
            pass
    
        for each_player in players_list:
            setattr(PlayerSelectionForm, each_player, BooleanField(label=each_player))
    
        setattr(PlayerSelectionForm, 'Confirm', SubmitField('Confirm Selection') )
        
        return PlayerSelectionForm() 
    
    
#### -------------------------------------- ##### 


############# Cap_Vc Selection Form
class Cap_Vc_SelectionForm(FlaskForm): 
    
    captain = SelectField(u'Select your Captain (x2 pts): ') 
    vice_captain = SelectField(u'Select your Vice Captain (x1.5 pts): ') 
    submit = SubmitField('Next')  

######## ------------------------------------------------------#### 

class FinalizeSquadForm(FlaskForm):    
    submit = SubmitField('Submit')   

#### -------------------------------------- #####

class EditSquadForm(FlaskForm): 
    edit_squad = SubmitField ('Edit Squad') 

#### -------------------------------------- #####