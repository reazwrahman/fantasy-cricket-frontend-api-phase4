from flask import render_template, redirect, request, url_for, flash, session
from flask_login import current_user 
from ast import literal_eval 
from datetime import datetime, timedelta
from pytz import timezone 
from flask import jsonify 
import json

from . import fantasyContest
from .. import db
from ..models import GameDetails, User 
from .forms import ActviveContestantsForm, ActiveGamesForm, ViewDetailsForm

from ..api.FantasyPointsDisplayHelper import FantasyPointsDisplayHelper 
from ..api.MatchPredictionHelper import MatchPredictionHelper
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

@fantasyContest.route('/getActiveGames', methods=['GET'])
def getActiveGames(): 
    active_games_list = dynamo_access.GetActiveGamesByIdTitleImage() 
    active_games = display_helper.transform_active_games(active_games_list)

    return jsonify(active_games), 200

@fantasyContest.route('/displayContestRanking', methods=['GET'])
def displayContestRanking():   
    match_id = request.args['match_id']  
    game_title = dynamo_access.GetGameTitle(match_id) 
    active_contestants = dynamo_access.GetActiveContestantsByUserNames(match_id) 
    match_result = dynamo_access.GetMatchResult(match_id)

    ## check if database has rankings updated yet
    fantasy_ranking = dynamo_access.GetFantasyRanking(match_id)  

    if not fantasy_ranking: 
        response = {
        "status": "206",
        "message": "No ranking available", 
        "data": active_contestants
        }
        return jsonify(response), 206
    
    else: 
        fantasy_ranking:dict = display_helper.convertRankingToDict(fantasy_ranking)  
        last_updated = dynamo_access.GetLastPointsUpdateTime(match_id)  
        time_delta_message = display_helper.GetTimeDeltaMessage(last_updated)  
        fantasy_ranking["last_updated"] = time_delta_message
        if match_result != 'unknown':  
            fantasy_ranking:dict = display_helper.AddMedalsToRanking(fantasy_ranking)
         
        return jsonify(fantasy_ranking)


@fantasyContest.route('/displayFullSquadSummary', methods=['GET'])
def displayFullSquadSummary():   
    match_id = request.args['match_id'] 
    user_id = request.args['user_id']  
    user_name = request.args['user_name']
    game_title = dynamo_access.GetGameTitle(match_id) 
    match_summary_points = dynamo_access.GetMatchSummaryPoints(match_id)  
    
    ## match result and prediciton points
    match_prediction_helper = MatchPredictionHelper(match_id) 
    prediction_dict = match_prediction_helper.GetOptionsDict()   
    match_result = dynamo_access.GetMatchResult(match_id) 
    match_prediction = dynamo_access.GetUserMatchPrediction(match_id, user_id)
    match_prediction_translated = prediction_dict[match_prediction]  
    prediction_bonus = " 0 points"
    if match_result == match_prediction: 
        prediction_bonus = "100 points" 


    if not match_summary_points:
        response = {
        "status": "error",
        "message": "No ranking available"
        }
        return jsonify(response), 404

        
    squad_selection = dynamo_access.GetUserSelectedSquad(match_id, user_id)  
    summary = display_helper.CreateSummaryPointsDisplay(match_summary_points, squad_selection)
    summary_points_display = summary[0] 
    total_points = summary[1]
    if prediction_bonus == "100 points": 
        total_points +=100

    df_display= {  
                'headings' : display_helper.GetSummaryPointsHeader(), 
                'rows' : summary_points_display,
                'total_points': total_points,
                'user_name': user_name, 
                'game_title': game_title, 
                'match_prediction': match_prediction_translated, 
                'prediction_bonus': prediction_bonus
                } 
    return jsonify(df_display),200



@fantasyContest.route('/displayPointsBreakdown', methods=['GET', 'POST'])
def displayPointsBreakdown():    
    try: 
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

        return jsonify(df_display), 200 
    
    except: 
        response = {
        "status": "error",
        "message": "server side error"
        }
        return jsonify(response), 500
