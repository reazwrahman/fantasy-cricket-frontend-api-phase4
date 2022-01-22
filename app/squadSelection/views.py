from numpy import full
from flask import render_template, redirect, request, url_for, flash, session
from flask_login import current_user, login_required 
from ast import literal_eval 
from datetime import datetime, timedelta
from pytz import timezone 

from . import squadSelection
from .. import db
from ..models import GameDetails, SelectedSquad
from .forms import ActiveGamesForm, PlayerSelectionFormFactory, FinalizeSquadForm, ContinueButton, Cap_Vc_SelectionForm 

from .ListOfAllPlayers import AllPlayers 



@squadSelection.route('/displayNavigations', methods=['GET', 'POST']) 
@login_required 
def displayNavigations(): 
    return render_template ('squadSelection/squadSelectionHomePage.html')


@squadSelection.route('/', methods=['GET', 'POST']) 
@login_required 
def DisplayActiveGames():  
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
        __updatePlayingXiLinkInDB__(selected_game_id) ## update to playing xi link, if possible
        return redirect(url_for('squadSelection.remindTheRules'))

    return render_template('squadSelection/displayActiveGames.html',form=form)


@squadSelection.route('/remindTheRules', methods=['GET', 'POST'])  
@login_required 
def remindTheRules(): 

    display_dict={ 
    'points_per_run':1,  
    'points_per_wicket':20, 
    'points_per_catch':10  
    }

    match_id = session.get('selected_game_id')  

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(match_id)   

    if (is_window_open == False): 
        return render_template ('squadSelection/gameExpiredPage.html')  

    else: 
        game_object=GameDetails.query.filter_by(match_id=match_id).first()   

        display_dict['points_per_run'] = game_object.points_per_run  
        display_dict['points_per_wicket'] = game_object.points_per_wicket   

        form= ContinueButton() 
        if form.validate_on_submit():  
            return redirect(url_for('squadSelection.selectBatters')) 
        
        return render_template ('squadSelection/remindTheRules.html',time_left=time_left,
                                display_dict=display_dict, form=form)


@squadSelection.route('/selectBatters', methods=['GET', 'POST'])  
@login_required 
def selectBatters():   
    instruction_header='Select at least 4 (and no more than 7) batsmen from the options below: '  

    ## query in the database for the squad_link 
    selected_match_id = session.get('selected_game_id') 

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(selected_match_id)    

    if (is_window_open == False): 
        return render_template ('squadSelection/gameExpiredPage.html')

    else:
        ## get the list of all batters  
        squad_link = GameDetails.query.filter_by(match_id=selected_match_id).first().squad_link  
        squad_object=AllPlayers(squad_link)
        batters= squad_object.GetAllBatters()

        ## create a form with possible batters choices
        formForBatters = PlayerSelectionFormFactory.BuildSimpleForm(batters)  

        ## collect user's selection for batsmen
        batterSelections=[] 
        if formForBatters.validate_on_submit(): 
            for eachBatter in (batters):
                if (getattr(formForBatters, eachBatter).data): 
                    batterSelections.append(eachBatter)  
            
            ## check if at least 4 batsmen have been chosen, if not reload the page with an error header  
            if len(batterSelections)<4 or len(batterSelections)>7:  
                flash('Invalid number of batsmen chosen, choose anywhere between 4 to 7 players')

            else:        
                session['selected_batters']=batterSelections
                return redirect(url_for('squadSelection.selectBowlers',selected_batters=session['selected_batters']))

        return render_template('squadSelection/playerSelectionPage.html',instruction=instruction_header, 
                                    time_left=time_left,form=formForBatters)    



@squadSelection.route('/selectBowlers', methods=['GET', 'POST'])  
@login_required 
def selectBowlers():   
    instruction_header='Select at least 4 (and no more than 7) bowlers from the options below: ' 
 
    ## get all the available bowlers ##
    ## query in the database for the squad_link 
    selected_match_id = session.get('selected_game_id') 

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(selected_match_id)   

    if (is_window_open == False): 
        return render_template ('squadSelection/gameExpiredPage.html')

    else:

        ## Get All available bowlers
        squad_link = GameDetails.query.filter_by(match_id=selected_match_id).first().squad_link  
        batterSelections=session.get('selected_batters')
        squad_object=AllPlayers(squad_link)
        bowlers= squad_object.GetAllBowlers() 

        formForBowlers = PlayerSelectionFormFactory.BuildSimpleForm(bowlers)  
        
        ## collect user's selection for bowlers
        bowlerSelections=[] 
        if formForBowlers.validate_on_submit(): 
            for eachbowler in (bowlers):
                if (getattr(formForBowlers, eachbowler).data): 
                    bowlerSelections.append(eachbowler)  
            
            ## check if at least 4 bowlers have been chosen, if not reload the page with an error header  
            if len(bowlerSelections)<4 or len(bowlerSelections)>7:  
                flash('Invalid number of bowlers chosen, choose anywhere between 4 to 7 players')
            
            if (len(batterSelections+bowlerSelections))>11: 
                flash('You have chosen more than 11 players, Select at most 11 players in your squad')
            
            else:        
                full_squad=batterSelections+bowlerSelections 
                session['full_squad']=full_squad
                return redirect(url_for('squadSelection.selectCapAndVc',full_squad=session['full_squad']))
        
        return render_template('squadSelection/playerSelectionPage.html',instruction=instruction_header, 
                            time_left=time_left, form=formForBowlers)   


@squadSelection.route('/selectCapAndVc', methods=['GET', 'POST']) 
@login_required 
def selectCapAndVc():  
    match_id=session.get('selected_game_id')  

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(match_id) 

    if (is_window_open == False): 
            return render_template ('squadSelection/gameExpiredPage.html')

    else:
        full_squad=session.get('full_squad')    

        form=Cap_Vc_SelectionForm()    
        squad_tuple=[] 
        for each in full_squad: 
            squad_tuple.append((each,each))

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
                return redirect(url_for('squadSelection.finalizeSquad'))

        return render_template('squadSelection/captainAndVcSelectionPage.html', 
                            time_left=time_left,form=form)
        


@squadSelection.route('/finalizeSquad', methods=['GET', 'POST']) 
@login_required 
def finalizeSquad(): 
    ## get session data 
    full_squad=session.get('full_squad')   
    Cap_Vc_Dict=session.get('Cap_Vc_Dict')  
    match_id=session.get('selected_game_id') 

    ## see how much time is left, or if it has expired already 
    is_window_open, time_left = __getTimeLeftIndicator__(match_id)  

    if (is_window_open == False): 
        return render_template ('squadSelection/gameExpiredPage.html')

    else:
        form=FinalizeSquadForm() 
        if form.validate_on_submit():  
            existing_record = SelectedSquad.query.filter_by(user_id=current_user.id, 
                                                        match_id=match_id).first() 
            if existing_record is None: 
                fantasy_squad=SelectedSquad(user_id=current_user.id, 
                                        match_id=match_id, 
                                        selected_squad=str(full_squad), 
                                        captain=Cap_Vc_Dict['captain'], 
                                        vice_captain=Cap_Vc_Dict['vice_captain'])
                db.session.add(fantasy_squad) 
                db.session.commit() 
                flash('Congrats! Your squad has been submitted') 
                return redirect(url_for('main.index'))
            else: 
                existing_record.selected_squad = str(full_squad)  
                existing_record.captain=Cap_Vc_Dict['captain'] 
                existing_record.vice_captain=Cap_Vc_Dict['vice_captain']
                db.session.commit()
                flash('Your squad has been successfully updated!') 
                return redirect(url_for('main.index'))
                
        return render_template('squadSelection/SquadSelectionResult.html', 
                            time_left=time_left,selections=full_squad,Cap_Vc_Dict=Cap_Vc_Dict, 
                            form=form)   


@squadSelection.route('/viewMySquad_Part1', methods=['GET', 'POST'])  
@login_required 
def viewMySquad_Part1(): 
    active_games_query = GameDetails.query.filter_by(game_status = 'Active')
    active_games_all=active_games_query.all()
    
    active_games_list=[]
    for each in active_games_all: 
        active_games_list.append((each.match_id,each.game_title))
    
    form= ActiveGamesForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id=form.game_selection.data 
        __updatePlayingXiLinkInDB__(selected_game_id)
        return redirect(url_for('squadSelection.viewMySquad_Part2',match_id=selected_game_id))

    return render_template('squadSelection/displayActiveGames.html',form=form)  


@squadSelection.route('/viewMySquad_Part2', methods=['GET', 'POST'])  
@login_required 
def viewMySquad_Part2(): 
    match_id=request.args['match_id']  

    game_object=GameDetails.query.filter_by(match_id=match_id).first()   
    squad_object=SelectedSquad.query.filter_by(match_id=match_id, 
                                            user_id=current_user.id).first() 

    if squad_object is not None:
        display_dict={
                    'full_squad': literal_eval(squad_object.selected_squad),
                    'captain': squad_object.captain,
                    'vice_captain': squad_object.vice_captain  
                    } 
        display_dict['full_squad'] = __indicatePlayingXiInSquad__(game_object.squad_link,display_dict['full_squad'])
        return render_template('squadSelection/viewMySquad.html',display_dict=display_dict)   
    else: 
        return render_template('squadSelection/NoSquadFound.html')


def __indicatePlayingXiInSquad__(squad_link,given_squad):
    if 'match-playing-xi' in squad_link:   
        modified_squad=[]
        squad_generator = AllPlayers(squad_link) 
        playing_xi = squad_generator.GetFullSquad()  

        for each in given_squad:  
            first_name = each.split(' ')[0] 
            last_name = each.split(' ')[1]  
            playing=False
            for each_playing_member in playing_xi: 
                if first_name in each_playing_member and last_name in each_playing_member: 
                    playing=True
                    break     
            if (playing): 
                modified_squad.append(each + '  (in playing-xi)')  
            else: 
                modified_squad.append(each + '  (!!! NOT in playing-xi !!!)') 

        return modified_squad
    ## if match_playing_xi not out yet, just return what was receieved
    else: 
        return given_squad



def __getTimeLeftIndicator__(match_id):  
    ## get the match start time from database 
    game_start_time_string = GameDetails.query.filter_by(match_id=match_id).first().game_start_time
    game_start_time_list = literal_eval(game_start_time_string)   
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
    


def __updatePlayingXiLinkInDB__(match_id): 
    if (__checkIfGameIsAboutToStart__(match_id)): 
        game_object = GameDetails.query.filter_by(match_id=match_id).first()   
        squad_link = game_object.squad_link 

        if 'match-playing-xi' not in squad_link:  
            playing_xi_link = __convertSquadLinkToPlayingXiLink__(squad_link)  
            if (__checkPlayingXiLinkValidity__(playing_xi_link)):  
                game_object.squad_link = playing_xi_link 
                db.session.commit()
            


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

def __convertSquadLinkToPlayingXiLink__(squad_link):  
    target_link=''  
    
    ## remove trailing slash if it's there
    if squad_link[len(squad_link)-1]=='/': 
        squad_link=squad_link[0:len(squad_link)-1] 
    #match-playing-xi
    url_split_list= squad_link.split('/') 
    url_split_list[len(url_split_list)-1]='match-playing-xi'  
    
    for each in url_split_list: 
        target_link += each+'/' 
    
    return target_link


def __checkPlayingXiLinkValidity__(playing_xi_link):  
    ## link is valid, if we can generate full squad with 22 players in it, otherwise 
    ## something is wrong 
    squad_generator=AllPlayers(playing_xi_link)
    try:  
        full_squad=squad_generator.GetFullSquad()   
        if len(full_squad) ==22:  
            return True 
        else:  
            return False 
    except:  
        return False




     
