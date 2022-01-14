from flask import render_template, redirect, request, url_for, flash, session

from . import gameSetup
from .. import db
from ..models import GameDetails
from .forms import GameSetupForm, ActiveGamesForm, AddScoreCardForm, DeactivateGameForm, UpdateGameDetailsForm



@gameSetup.route('/', methods=['GET', 'POST'])
def SetupGame():
    form = GameSetupForm()
    if form.validate_on_submit():  
        match_exists = GameDetails.query.filter_by(match_id=form.match_id.data).first() 
        if match_exists is None:
            game_details = GameDetails(game_title=form.game_title.data, 
                        match_id=form.match_id.data,
                        game_status=form.game_status.data,
                        squad_link=form.squad_link.data, 
                        game_start_time=form.game_start_time.data)
            db.session.add(game_details)
            db.session.commit()
            flash('Game details have been stored in  database')
            return redirect(url_for('gameSetup.AddScoreCard_Part1')) 
        else: 
            flash('Sorry, Database already Contains a record with this match id')
    return render_template('gameSetup/setupGame.html',form=form)



@gameSetup.route('/AddScoreCard_Part1', methods=['GET', 'POST'])
def AddScoreCard_Part1(): 
    active_games_query = GameDetails.query.filter_by(game_status = 'Active')
    active_games_all=active_games_query.all()
    
    active_games_list=[]
    for each in active_games_all: 
        active_games_list.append((each.match_id,each.game_title))
    
    form= ActiveGamesForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id=form.game_selection.data  
        session['selected_game_id']=selected_game_id
        return redirect(url_for('gameSetup.AddScoreCard_Part2'))

    return render_template('gameSetup/displayActiveGames.html',form=form)


@gameSetup.route('/AddScoreCard_Part2', methods=['GET', 'POST'])
def AddScoreCard_Part2(): 
    match_id = session.get('selected_game_id') 
    game_object = GameDetails.query.filter_by(match_id=match_id).first()

    form =  AddScoreCardForm()  
    if form.validate_on_submit(): 
        game_object.scorecard_link = form.score_card_link.data   
        game_object.points_per_run = form.points_per_run.data 
        game_object.points_per_wicket = form.points_per_wicket.data
        db.session.commit()  
        flash('Additional Game Details have been successfully updated in database') 
    
    return render_template('gameSetup/addScoreCard.html', game_title=game_object.game_title, form=form) 


@gameSetup.route('/DeactivateGame', methods=['GET', 'POST'])
def DeactivateGame(): 
    active_games_query = GameDetails.query.filter_by(game_status = 'Active')
    active_games_all=active_games_query.all()
    
    active_games_list=[]
    for each in active_games_all: 
        active_games_list.append((each.match_id,each.game_title))
    
    form= DeactivateGameForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id = form.game_selection.data  
        game_object = GameDetails.query.filter_by(match_id = selected_game_id).first() 

        db.session.delete(game_object)
        db.session.commit() 
        flash('Selected Game has been Deactivated')

    return render_template('gameSetup/displayActiveGames.html',form=form) 

@gameSetup.route('/UpdateGameDetails', methods=['GET', 'POST'])
def UpdateGameDetails(): 
    active_games_query = GameDetails.query.filter_by(game_status = 'Active')
    active_games_all=active_games_query.all()
    
    active_games_list=[]
    for each in active_games_all: 
        active_games_list.append((each.match_id,each.game_title))
    
    form= UpdateGameDetailsForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id = form.game_selection.data  
        game_object = GameDetails.query.filter_by(match_id = selected_game_id).first()  
        squad_link=form.updated_squad_link.data 
        game_start_time=form.game_start_time.data

        if len(squad_link) > 5:  ## just an arbitrary value to make sure it's not an empty string
            game_object.squad_link=squad_link
            db.session.commit()  
            flash ('Link for Potential Squad has been Updated') 

        if len(game_start_time) > 5:   ## just an arbitrary value to make sure it's not an empty string
            game_object.game_start_time=game_start_time
            db.session.commit()  
            flash ('Game Start Time Updated')

    return render_template('gameSetup/updateGameDetails.html',form=form)

