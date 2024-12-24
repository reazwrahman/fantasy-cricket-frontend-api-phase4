from numpy import full
from flask import render_template, redirect, request, url_for, flash, session, jsonify
from flask_login import current_user, login_required
from ast import literal_eval
from datetime import datetime, timedelta
from pytz import timezone 
from ast import literal_eval 
from typing import List, Dict

from . import squadSelection
from .. import db
from ..models import GameDetails
from ..models import User
from ..DynamoAccess import DynamoAccess
from app.api.SquadGenerator.SquadOperators import SquadOperators
from app.api.MatchPredictionHelper import MatchPredictionHelper
from app.api.AuthHelper import AuthHelper

dynamo_access = DynamoAccess()
auth_helper = AuthHelper()


@squadSelection.route('/fullMatchSquad', methods=['GET'])
def getFullMatchSquad():
   
    ## query in the database for the squad_link
    selected_match_id:str = request.args['match_id'] 
  
    ## get the list of all batters
    match_squad = dynamo_access.GetMatchSquad(selected_match_id) 
    game_start_time:str = __convert_to_milliseconds(dynamo_access.GetGameStartTime(selected_match_id))
    squad_operator = SquadOperators(match_squad) 

    batters_dict= squad_operator.GetAllBatters()
    bowlers_dict= squad_operator.GetNonOverlappingPlayers(batters_dict)

    match_prediction_helper = MatchPredictionHelper(selected_match_id)
    match_predictions:Dict[str,str] = match_prediction_helper.GetAllOptions()

    full_squad = {   
                'start_time': game_start_time, 
                'batters' : __transform_players_dict(batters_dict), 
                'bowlers' : __transform_players_dict(bowlers_dict), 
                'predictions': match_predictions
                } 

    return jsonify(full_squad), 200 


@squadSelection.route("/viewMySquad", methods=["POST"])
def viewMySquad():
    print("hello world")
    data = request.get_json()
    email = data["email"]
    user_id = data["user_id"]
    match_id = data["match_id"]
    token = request.headers.get("Authorization") 

    user: User = dynamo_access.GetUserByEmail(email)

    if not token or not auth_helper.validate_jwt(token=token, user_email=email):
        return jsonify({"error": "Invalid authorization token"}), 403 
    
    if user.id != user_id: 
        return jsonify({"error": "You are not authorized to view this resource"}), 403

    squad_selection = dynamo_access.GetUserSelectedSquad(match_id, user_id)
    match_squad = dynamo_access.GetMatchSquad(match_id)
    match_prediction_helper = MatchPredictionHelper(match_id)
    prediction_dict = match_prediction_helper.GetOptionsDict()

    if squad_selection is not None:
        selected_squad = squad_selection["selected_squad"]
        captain = squad_selection["captain"]
        vice_captain = squad_selection["vice_captain"]
        ## get playername from id
        match_squad = dynamo_access.GetMatchSquad(match_id)
        squad_operator = SquadOperators(match_squad)

        selected_squad_names = squad_operator.GetNamesListFromIds(
            selected_squad, match_squad
        )
        selected_squad_names = squad_operator.AttachPlayingXiTagToNames(
            selected_squad_names, match_squad
        )
        captain_name = match_squad[captain]["Name"]
        vc_name = match_squad[vice_captain]["Name"]
        result_prediction = prediction_dict[squad_selection["result_prediction"]]
        squad_by_names = selected_squad_names
        display_dict = {
            "full_squad": squad_by_names,
            "captain": captain_name,
            "vice_captain": vc_name,
            "result_prediction": result_prediction,
        }
        return jsonify(display_dict), 200
    else:
        return jsonify({"error": "Squad not found for the given user."}), 404


def __convert_to_milliseconds(time:str):   
    timestamp:list[int] = literal_eval(time)
    timestamp.append(0)  # add seconds 

    timestamp = datetime(*timestamp)
    # Get the milliseconds timestamp
    milliseconds_timestamp = int(timestamp.timestamp() * 1000)

    return milliseconds_timestamp 

def __transform_players_dict(players_dict:dict):  
    result:list[dict] = []
    for each in players_dict: 
        new_dict:dict = dict() 
        new_dict["id"] = each 
        new_dict.update(players_dict[each]) 
        result.append(new_dict) 
    
    return result


