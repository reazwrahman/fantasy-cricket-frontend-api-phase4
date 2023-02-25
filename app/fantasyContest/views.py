from flask import render_template, redirect, request, url_for, flash, session
from flask_login import current_user 
from ast import literal_eval 
from datetime import datetime, timedelta
from pytz import timezone 

from . import fantasyContest
from .. import db
from ..models import GameDetails, User 
from .forms import ActviveContestantsForm, ActiveGamesForm, ViewDetailsForm

from ..api.FantasyPointsDisplayHelper import FantasyPointsDisplayHelper
from ..DynamoAccess import DynamoAccess  

dynamo_access = DynamoAccess() 
display_helper = FantasyPointsDisplayHelper() 


@fantasyContest.route('/', methods=['GET', 'POST'])
def displayActiveGames(): 
    active_games_list = dynamo_access.GetActiveGamesByIdAndTitle()
    
    form= ActiveGamesForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id=form.game_selection.data   
        return redirect(url_for('fantasyContest.displayContestRanking', match_id=selected_game_id))

    return render_template('fantasyContest/displayActiveGames.html',form=form) 

@fantasyContest.route('/displayContestRanking', methods=['GET', 'POST'])
def displayContestRanking():   
    match_id = request.args['match_id']  
    game_title = dynamo_access.GetGameTitle(match_id) 
    active_contestants = dynamo_access.GetActiveContestantsByUserNames(match_id)

    ## check if database has rankings updated yet
    fantasy_ranking = dynamo_access.GetFantasyRanking(match_id)
    print(fantasy_ranking)
    if not fantasy_ranking:
        return render_template('fantasyContest/waitForScorecardPage.html', active_contestants=active_contestants) 
    
    else:  
        user_selection_tuples=[]  
        user_selection_dict = {}
        for each in fantasy_ranking:                                          
                user_selection_tuples.append((each[-1],each[1])) ##user_id, user_name
                user_selection_dict[each[-1]] = each[1] # {user_id: user_name}

        form= ActviveContestantsForm() 
        form.user_selection.choices=user_selection_tuples 
        if form.validate_on_submit():  
            user_id = form.user_selection.data    
            user_name = user_selection_dict[user_id]
            return redirect (url_for('fantasyContest.displayFullSquadSummary',  
                                     match_id=match_id, user_id=user_id, 
                                     user_name = user_name))

        fantasy_ranking_modified = display_helper.HideUserIdFromRanking(fantasy_ranking)
        print(fantasy_ranking_modified) 
        print(game_title)
        return render_template('fantasyContest/displayContestRanking.html', game_title=game_title,ranked_contestants=fantasy_ranking_modified, form=form)


@fantasyContest.route('/displayFullSquadSummary', methods=['GET', 'POST'])
def displayFullSquadSummary():   
    match_id = request.args['match_id'] 
    user_id = request.args['user_id']  
    user_name = request.args['user_name']
    game_title = dynamo_access.GetGameTitle(match_id) 
    match_summary_points = dynamo_access.GetMatchSummaryPoints(match_id) 

    if not match_summary_points:
        return render_template('fantasyContest/waitForScorecardPage.html', active_contestants=[]) 

    
    form = ViewDetailsForm()     

    squad_selection = dynamo_access.GetUserSelectedSquad(match_id, user_id)  
    summary = display_helper.CreateSummaryPointsDisplay(match_summary_points, squad_selection)
    summary_points_display = summary[0] 
    total_points = summary[1]

    df_display= {  
                'headings' : display_helper.GetSummaryPointsHeader(), 
                'rows' : summary_points_display,
                'total_points': total_points,
                'user_name': user_name, 
                'game_title': game_title
                } 
    if form.validate_on_submit(): 
        return redirect(url_for('fantasyContest.displayPointsBreakdown', match_id=match_id,  
                                user_id=user_id, user_name=user_name))

    return render_template("fantasyContest/viewFantasyPointSummary.html", df_display=df_display, 
                                form=form) 



@fantasyContest.route('/displayPointsBreakdown', methods=['GET', 'POST'])
def displayPointsBreakdown():   
    match_id = request.args['match_id']  
    user_id = request.args['user_id']
    user_name = request.args['user_name']   
    game_title = dynamo_access.GetGameTitle(match_id) 

    squad_selection = dynamo_access.GetUserSelectedSquad(match_id, user_id)

    batting_points = dynamo_access.GetMatchBreakdownPoints(match_id, 'batting_points')
    bowling_points = dynamo_access.GetMatchBreakdownPoints(match_id, 'bowling_points')
    fielding_points = dynamo_access.GetMatchBreakdownPoints(match_id, 'fielding_points') 

    batting_display = display_helper.CreateBreakdownPointsDisplay(batting_points, squad_selection)
    bowling_display = display_helper.CreateBreakdownPointsDisplay(bowling_points, squad_selection) 
    fielding_display = display_helper.CreateBreakdownPointsDisplay(fielding_points, squad_selection)

    df_display= {   
                'game_title' : game_title,
                'user_name': user_name,
                'batting_display' : {
                                    'headings' : display_helper.GetBreakdownPointsHeader(), 
                                    'rows' : batting_display[0], 
                                    'total_points': batting_display[1]
                                    },
                                    
                'bowling_display' : { 
                                    'headings' : display_helper.GetBreakdownPointsHeader(), 
                                    'rows' : bowling_display[0], 
                                    'total_points': bowling_display[1] 
                                    },
                                    

                'fielding_display' : { 
                                    'headings' : display_helper.GetBreakdownPointsHeader(), 
                                    'rows' : fielding_display[0], 
                                    'total_points': fielding_display[1]
                                    } 
        
                } 

    return render_template('fantasyContest/fantasyPointsBreakdown.html', df_display=df_display) 

