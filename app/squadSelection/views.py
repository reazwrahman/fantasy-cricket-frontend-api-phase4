from numpy import full
from flask import render_template, redirect, request, url_for, flash, session
from flask_login import current_user, login_required 
from ast import literal_eval 
from datetime import datetime, timedelta
from pytz import timezone 

from . import squadSelection
from .. import db
from ..models import GameDetails
from .forms import ActiveGamesForm, PlayerSelectionFormFactory, FinalizeSquadForm, ContinueButton, Cap_Vc_SelectionForm 


from ..DynamoAccess import DynamoAccess 
from app.api.SquadGenerator.SquadOperators import SquadOperators

dynamo_access = DynamoAccess() 

@squadSelection.route('/displayNavigations', methods=['GET', 'POST']) 
@login_required 
def displayNavigations(): 
    return render_template ('squadSelection/squadSelectionHomePage.html')


@squadSelection.route('/', methods=['GET', 'POST']) 
@login_required 
def DisplayActiveGames():  
    active_games_list = dynamo_access.GetActiveGamesByIdAndTitle()
    
    form= ActiveGamesForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id=form.game_selection.data  
        session['selected_game_id']=selected_game_id 
        return redirect(url_for('squadSelection.remindTheRules'))

    return render_template('squadSelection/displayActiveGames.html',form=form)


@squadSelection.route('/remindTheRules', methods=['GET', 'POST'])  
@login_required 
def remindTheRules():  
    match_id = session.get('selected_game_id') 
    scorecard_info = dynamo_access.GetScorecardInfo(match_id) 

    display_dict={ 
    'points_per_run':scorecard_info['points_per_run'],  
    'points_per_wicket':scorecard_info['points_per_wicket'], 
    'points_per_catch':10  
    } 

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(match_id)   

    if (not is_window_open): 
        return render_template ('squadSelection/gameExpiredPage.html')  

    else: 
        form= ContinueButton() 
        if form.validate_on_submit():  
            return redirect(url_for('squadSelection.selectBatters')) 
        
        return render_template ('squadSelection/remindTheRules.html',time_left=time_left,
                                display_dict=display_dict, form=form)


@squadSelection.route('/selectBatters', methods=['GET', 'POST'])  
@login_required 
def selectBatters():   
    instruction_header='Select at least 3 (and no more than 7) batsmen from the options below: '  

    ## query in the database for the squad_link 
    selected_match_id = session.get('selected_game_id')   

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(selected_match_id)    

    if (not is_window_open): 
        return render_template ('squadSelection/gameExpiredPage.html')

    else: 
        ## get the list of all batters  
        match_squad = dynamo_access.GetMatchSquad(selected_match_id) 
        squad_operator = SquadOperators(match_squad) 

        batters_dict= squad_operator.GetAllBatters() 
        batter_names = squad_operator.GetPlayerNamesFromDict(batters_dict) 
        reversed_dict = squad_operator.GetReversedDict(batters_dict)

        batter_names_with_playing_xi_tag = squad_operator.AttachPlayingXiTagToNames(batter_names, match_squad) 

        ## create a form with possible batters choices
        formForBatters = PlayerSelectionFormFactory.BuildSimpleForm(batter_names_with_playing_xi_tag)  

        ## collect user's selection for batsmen
        batterSelections=[] 
        if formForBatters.validate_on_submit(): 
            for eachBatter in (batter_names):
                if (getattr(formForBatters, eachBatter).data): 
                    batter_name_without_playing_xi_tag = squad_operator.RemovePlayingXiTagFromName(eachBatter)  
                    batterSelections.append(reversed_dict[batter_name_without_playing_xi_tag])
            
            ## check if at least 4 batsmen have been chosen, if not reload the page with an error header  
            if len(batterSelections) < 3 or len(batterSelections) > 7:  
                flash('Invalid number of batsmen chosen, choose anywhere between 3 to 7 players')

            else: 
                session['selected_batters']=batterSelections
                session['match_squad']=match_squad
                return redirect(url_for('squadSelection.selectBowlers', match_squad = session['match_squad'], 
                                        selected_batters=session['selected_batters']))

        return render_template('squadSelection/playerSelectionPage.html',instruction=instruction_header, 
                                    time_left=time_left,form=formForBatters)    



@squadSelection.route('/selectBowlers', methods=['GET', 'POST'])  
@login_required 
def selectBowlers():   
    instruction_header='Select at least 3 (and no more than 7) bowlers from the options below: ' 
    ## get session variables 
    selected_match_id = session.get('selected_game_id')   
    batterSelections = session.get('selected_batters') 
    match_squad = session.get('match_squad')

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(selected_match_id)   

    if (is_window_open == False): 
        return render_template ('squadSelection/gameExpiredPage.html')

    else:

        ## get all the available non-batters ##
        squad_operator = SquadOperators(match_squad)

        batters_dict= squad_operator.GetAllBatters()
        non_batters_dict= squad_operator.GetNonOverlappingPlayers(batters_dict) 
        player_names = squad_operator.GetPlayerNamesFromDict(non_batters_dict)  
        reversed_dict = squad_operator.GetReversedDict(non_batters_dict) 

        player_names_with_playing_xi_tag = squad_operator.AttachPlayingXiTagToNames(player_names, match_squad)

        formForBowlers = PlayerSelectionFormFactory.BuildSimpleForm(player_names_with_playing_xi_tag)  
        
        ## collect user's selection for bowlers
        bowlerSelections=[] 
        if formForBowlers.validate_on_submit(): 
            for eachbowler in (player_names):
                if (getattr(formForBowlers, eachbowler).data):  
                    player_name = squad_operator.RemovePlayingXiTagFromName(eachbowler)
                    bowlerSelections.append(reversed_dict[player_name])  
            
            ## check if at least 3 bowlers have been chosen, if not reload the page with an error header  
            if len(bowlerSelections) < 3 or len(bowlerSelections) > 7:  
                flash('Invalid number of bowlers chosen, choose anywhere between 3 to 7 players')
            
            elif (len(batterSelections+bowlerSelections))>11: 
                flash('You have chosen more than 11 players, Select at most 11 players in your squad')
            
            else:        
                full_squad=batterSelections+bowlerSelections 
                session['full_squad']=full_squad 
                session['match_squad'] = match_squad
                return redirect(url_for('squadSelection.selectCapAndVc', 
                                        match_squad=session['match_squad'], 
                                        full_squad=session['full_squad']))
        
        return render_template('squadSelection/playerSelectionPage.html',instruction=instruction_header, 
                            time_left=time_left, form=formForBowlers)   


@squadSelection.route('/selectCapAndVc', methods=['GET', 'POST']) 
@login_required 
def selectCapAndVc():  
    ## get session variables
    match_id=session.get('selected_game_id')   
    full_squad=session.get('full_squad')  
    match_squad = session.get('match_squad')

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(match_id) 

    if (not is_window_open): 
            return render_template ('squadSelection/gameExpiredPage.html')

    else:   
        form=Cap_Vc_SelectionForm()    
        squad_tuple=[] 
        for each in full_squad: 
            squad_tuple.append((each,match_squad[each]['Name']))

        form.captain.choices= squad_tuple 
        form.vice_captain.choices= squad_tuple

        if form.validate_on_submit():   
            if form.captain.data == form.vice_captain.data: 
                flash('You must select different players for captain and vice captain') 
            else:  
                Cap_Vc_Dict={}
                Cap_Vc_Dict['captain']=form.captain.data 
                Cap_Vc_Dict['vice_captain']=form.vice_captain.data   
                session['Cap_Vc_Dict']=Cap_Vc_Dict
                return redirect(url_for('squadSelection.finalizeSquad', 
                                        cap_vc_dict=session['Cap_Vc_Dict']))

        return render_template('squadSelection/captainAndVcSelectionPage.html', 
                            time_left=time_left,form=form)
        


@squadSelection.route('/finalizeSquad', methods=['GET', 'POST']) 
@login_required 
def finalizeSquad(): 
    ## get session data 
    full_squad=session.get('full_squad')   
    Cap_Vc_Dict=session.get('Cap_Vc_Dict')  
    match_id=session.get('selected_game_id')  
    match_squad=session.get('match_squad') 
    squad_operator = SquadOperators(match_squad)

    full_squad_names = squad_operator.GetNamesListFromIds(full_squad, match_squad) 
    full_squad_names = squad_operator.AttachPlayingXiTagToNames(full_squad_names, match_squad)

    cap_vc_dict_names={'captain':match_squad[Cap_Vc_Dict['captain']]['Name'], 
                       'vice_captain': match_squad[Cap_Vc_Dict['vice_captain']]['Name']}

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(match_id)  

    if (is_window_open == False): 
        return render_template ('squadSelection/gameExpiredPage.html')

    else:
        form=FinalizeSquadForm() 
        if form.validate_on_submit():   
            fantasy_squad={ 'selected_squad': full_squad, 
                                'captain': Cap_Vc_Dict['captain'], 
                                'vice_captain': Cap_Vc_Dict['vice_captain'] 
                              } 
            dynamo_access.AddSelectedSquad(match_id, current_user.id, 'username'+str(current_user.id), fantasy_squad)    

            flash('Congrats! Your squad has been submitted') 
            return redirect(url_for('main.index'))
            
                
        return render_template('squadSelection/SquadSelectionResult.html', 
                            time_left=time_left,selections=full_squad_names,Cap_Vc_Dict=cap_vc_dict_names, 
                            form=form)   


@squadSelection.route('/viewMySquad_Part1', methods=['GET', 'POST'])  
@login_required 
def viewMySquad_Part1(): 
    active_games_list = dynamo_access.GetActiveGamesByIdAndTitle()
    
    form= ActiveGamesForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id=form.game_selection.data 
        return redirect(url_for('squadSelection.viewMySquad_Part2',match_id=selected_game_id))

    return render_template('squadSelection/displayActiveGames.html',form=form)  


@squadSelection.route('/viewMySquad_Part2', methods=['GET', 'POST'])  
@login_required 
def viewMySquad_Part2(): 
    match_id=request.args['match_id']  
    squad_selection = dynamo_access.GetUserSelectedSquad(match_id, current_user.id)  
    match_squad = dynamo_access.GetMatchSquad(match_id)
    
    if squad_selection is not None: 
        selected_squad = squad_selection['selected_squad'] 
        captain = squad_selection['captain'] 
        vice_captain = squad_selection['vice_captain']
        ## get playername from id 
        match_squad = dynamo_access.GetMatchSquad(match_id)
        squad_operator = SquadOperators(match_squad)

        selected_squad_names = squad_operator.GetNamesListFromIds(selected_squad, match_squad)  
        selected_squad_names = squad_operator.AttachPlayingXiTagToNames(selected_squad_names, match_squad)
        captain_name = match_squad[captain]['Name'] 
        vc_name = match_squad[vice_captain]['Name']
        squad_by_names = selected_squad_names
        display_dict={
                    'full_squad': squad_by_names,
                    'captain': captain_name,
                    'vice_captain': vc_name  
                    } 
        return render_template('squadSelection/viewMySquad.html',display_dict=display_dict)   
    else: 
        return render_template('squadSelection/NoSquadFound.html')



def __getTimeLeftIndicator__(match_id):  
    ## get the match start time from database 
    game_start_time = dynamo_access.GetGameStartTime(match_id) 
    game_start_time_list = literal_eval(game_start_time)   
    game_start_time= datetime(game_start_time_list[0], game_start_time_list[1],  
                              game_start_time_list[2],game_start_time_list[3], 
                              game_start_time_list[4],0,tzinfo=timezone('EST'))  

    # get the current eastern time 
    est_time_now=datetime.now(timezone('EST')) 
    if est_time_now>=game_start_time: 
        return False, "Sorry, Selection window for this Game has Closed Already"
    else:  
        delta=game_start_time-est_time_now 
        return True, f'Selection Window will Close in {delta} seconds' 
    


def __checkIfGameIsAboutToStart__(match_id, toss_time=30):  
    ## get the match start time from database 
    game_start_time_string = GameDetails.query.filter_by(match_id=match_id).first().game_start_time
    game_start_time_list = literal_eval(game_start_time_string)   
    game_start_time= datetime(game_start_time_list[0], game_start_time_list[1],  
                              game_start_time_list[2],game_start_time_list[3], 
                              game_start_time_list[4],0,tzinfo=timezone('EST'))  

    est_time_now= datetime.now(timezone('EST')) 
    minutes_delta=timedelta(minutes=toss_time) 

    if est_time_now > (game_start_time-minutes_delta): 
        return True 
    else: 
        return False 








     
