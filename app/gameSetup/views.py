from app.decorators import admin_required
from flask import render_template, redirect, request, url_for, flash, session 
from flask_login import login_required, current_user

from . import gameSetup
from .. import db
from ..models import GameDetails
from .forms import GameSetupForm, ActiveGamesForm, AddScoreCardForm, DeactivateGameForm, UpdateGameDetailsForm
from ..DynamoAccess import DynamoAccess 
from app.api.SquadGenerator.ListOfAllPlayers import AllPlayers 
from app.api.SquadGenerator.SquadOperators import SquadOperators

dynamo_access = DynamoAccess()

@gameSetup.route('/displayNavigations', methods=['GET', 'POST']) 
@admin_required
@login_required 
def displayNavigations(): 
    return render_template ('gameSetup/gameSetupHomePage.html')

@gameSetup.route('/', methods=['GET', 'POST']) 
@admin_required
@login_required 
def SetupGame():
    form = GameSetupForm()
    if form.validate_on_submit():  
        game_details = GameDetails(game_title=form.game_title.data, 
                    match_id=form.match_id.data,
                    game_status=form.game_status.data,
                    squad_link=form.squad_link.data, 
                    game_start_time=form.game_start_time.data) 
        
        ## add initial game info on database
        game_created = dynamo_access.CreateNewGame(game_details)
        
        ## add match squad to database 
        squad_generator = AllPlayers(game_details.squad_link)
        full_squad = squad_generator.GetFullSquad() 
        squad_created = dynamo_access.AddMatchSquad(game_details.match_id, full_squad) 

        if game_created and squad_created:  
            flash('Game details have been stored in  database') 
        else: 
            flash('ERROR Something went wrong while creating game or creating match squad') 

        return redirect(url_for('gameSetup.AddScoreCard_Part1')) 

    return render_template('gameSetup/setupGame.html',form=form)



@gameSetup.route('/AddScoreCard_Part1', methods=['GET', 'POST']) 
@admin_required
@login_required 
def AddScoreCard_Part1(): 
    active_games_list = dynamo_access.GetActiveGamesByIdAndTitle()
    
    form= ActiveGamesForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id=form.game_selection.data   

        print (selected_game_id)
        session['selected_game_id']=selected_game_id
        return redirect(url_for('gameSetup.AddScoreCard_Part2'))

    return render_template('gameSetup/displayActiveGames.html',form=form)


@gameSetup.route('/AddScoreCard_Part2', methods=['GET', 'POST']) 
@admin_required
@login_required 
def AddScoreCard_Part2(): 
    match_id = session.get('selected_game_id')  
    game_title = dynamo_access.GetGameTitle(match_id)

    form =  AddScoreCardForm()  
    if form.validate_on_submit(): 
        scorecard_details = {'scorecard_link': form.score_card_link.data, 
                            'points_per_run': form.points_per_run.data, 
                            'points_per_wicket': form.points_per_wicket.data
                         }
        update_successful = dynamo_access.AddScoreCardDetails(match_id, scorecard_details)
     
        if update_successful:
            flash('Additional Game Details have been successfully updated in database')  
            return redirect (url_for('gameSetup.displayNavigations')) 
        else: 
            flash('Something went wrong: couldnt add scorecard details to database')  
    
    return render_template('gameSetup/addScoreCard.html', game_title=game_title, form=form) 



@gameSetup.route('/DeactivateGame', methods=['GET', 'POST']) 
@admin_required
@login_required 
def DeactivateGame(): 
    active_games_list = dynamo_access.GetActiveGamesByIdAndTitle()
    
    form= DeactivateGameForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id = form.game_selection.data  
        deletion_succesful = dynamo_access.DeleteGame(selected_game_id) and dynamo_access.DeleteSquads(selected_game_id)
        if deletion_succesful: 
            flash('Selected Game has been Deactivated') 
        else: 
            flash('ERROR Something went wrong with the database while trying to delete')

    return render_template('gameSetup/displayActiveGames.html',form=form) 



@gameSetup.route('/UpdateGameDetails', methods=['GET', 'POST']) 
@admin_required
@login_required 
def UpdateGameDetails(): 
    active_games_list = dynamo_access.GetActiveGamesByIdAndTitle()
    
    form= UpdateGameDetailsForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id = form.game_selection.data    
        squad_link=form.updated_squad_link.data 
        game_start_time=form.game_start_time.data

        if len(squad_link) > 3:  ## just an arbitrary value to make sure it's not an empty string 
            dynamo_access.UpdateSquadLink(selected_game_id, squad_link) 
            squad_object = AllPlayers(squad_link) 

            if 'playing-xi' in squad_link: 
                playing_xi_squad = squad_object.GetFullSquad()  
                match_squad = dynamo_access.GetMatchSquad(selected_game_id) 
                squad_operator = SquadOperators(match_squad)
                updated_match_squad = squad_operator.AddPlayingXiIndicator(playing_xi_squad)
                
                ## update match squad to database 
                squad_created = dynamo_access.AddMatchSquad(selected_game_id, updated_match_squad) 
                if squad_created: flash ('Match Squad Has Been Updated With Playing XI Status') 
            else: 
                ## update whole match squad  
                match_squad = squad_object.GetFullSquad()  
                squad_created = dynamo_access.AddMatchSquad(selected_game_id, match_squad)  
                if squad_created: flash ('Match Squad Has Been Updated With the New Link') 
                


        if len(game_start_time) > 3:   ## to avoid empty or 'na' string
            dynamo_access.UpdateSquadLink(selected_game_id, game_start_time)  
            flash ('Game Start Time Updated')

    return render_template('gameSetup/updateGameDetails.html',form=form)

