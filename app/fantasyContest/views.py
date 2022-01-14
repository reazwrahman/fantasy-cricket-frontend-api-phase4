from flask import render_template, redirect, request, url_for, flash, session
from flask_login import current_user 
from ast import literal_eval

from . import fantasyContest
from .. import db
from ..models import GameDetails, SelectedSquad, User 
from .forms import ActviveContestantsForm, ActiveGamesForm, ViewDetailsForm

from .FantasyPointsCalculator_API.FantasyPointsCalculatorIF import FantasyPointsForFullSquad


@fantasyContest.route('/', methods=['GET', 'POST'])
def displayActiveGames(): 
    active_games_query = GameDetails.query.filter_by(game_status = 'Active')
    active_games_all=active_games_query.all()
    
    active_games_list=[]
    for each in active_games_all: 
        active_games_list.append((each.match_id,each.game_title))
    
    form= ActiveGamesForm() 
    form.game_selection.choices=active_games_list 

    if form.validate_on_submit(): 
        selected_game_id=form.game_selection.data  
        return redirect(url_for('fantasyContest.displayContestRanking', match_id=selected_game_id))

    return render_template('fantasyContest/displayActiveGames.html',form=form) 

@fantasyContest.route('/displayContestRanking', methods=['GET', 'POST'])
def displayContestRanking():   
    match_id = request.args['match_id'] 

    ## check if score card is available yet
    game_object=GameDetails.query.filter_by(match_id=match_id).first()   
    scorecard_link=game_object.scorecard_link 

    if scorecard_link == None or len(scorecard_link) < 5: ## just an arbitrary number to avoid empty string 
        return render_template('fantasyContest/waitForScorecardPage.html') 
    
    else:
        ranked_contestants = __rankContestants__ (match_id=match_id)  
        user_selection_tuples=[] 
        for each in ranked_contestants: 
                user_selection_tuples.append((each[1],each[1]))

        form= ActviveContestantsForm() 
        form.user_selection.choices=user_selection_tuples 
        if form.validate_on_submit():  
            user_name = form.user_selection.data   
            return redirect (url_for('fantasyContest.displayFullSquadSummary', match_id=match_id, user_name=user_name))

        return render_template('fantasyContest/experimental.html', ranked_contestants=ranked_contestants, form=form)


@fantasyContest.route('/displayFullSquadSummary', methods=['GET', 'POST'])
def displayFullSquadSummary():   
    match_id = request.args['match_id'] 
    user_name = request.args['user_name'] 
    ## check if score card is available yet
    game_object=GameDetails.query.filter_by(match_id=match_id).first()   
    scorecard_link=game_object.scorecard_link 

    if scorecard_link == None or len(scorecard_link) < 5: ## just an arbitrary number to avoid empty string 
        return render_template('fantasyContest/waitForScorecardPage.html') 
    
    else:
        form = ViewDetailsForm()     
        # first find the user id 
        user_id = User.query.filter_by(username=user_name).first().id
        Fantasy_Calculator = __getFantasyCalculatorObject__(match_id=match_id, user_id = user_id)
        full_squad_df=Fantasy_Calculator.GetFullSquadDf()  
    
        df_display= { 
                    'headings' : FantasyPointsForFullSquad.GetDfHeadingsList(full_squad_df), 
                    'rows' : FantasyPointsForFullSquad.GetDfRowsList(full_squad_df), 
                    'total_points': Fantasy_Calculator.GetTotalFantasyPoints(), 
                    'user_name': user_name
                    } 
        if form.validate_on_submit(): 
            return redirect(url_for('fantasyContest.displayPointsBreakdown', match_id=match_id, user_name=user_name))

        return render_template("fantasyContest/viewFantasyPointSummary.html", df_display=df_display, 
                                form=form) 





@fantasyContest.route('/viewMyFantasyPoint', methods=['GET', 'POST'])
def viewMyFantasyPoint(): 
    match_id = request.args['match_id'] 

    ## check if score card is available yet
    game_object=GameDetails.query.filter_by(match_id=match_id).first()   
    scorecard_link=game_object.scorecard_link 

    if scorecard_link == None or len(scorecard_link) < 5: ## just an arbitrary number to avoid empty string 
        return render_template('fantasyContest/waitForScorecardPage.html') 
    
    else: 
        form = ViewDetailsForm()   
        Fantasy_Calculator = __getFantasyCalculatorObject__(match_id=match_id, user_id = current_user.id)
        full_squad_df=Fantasy_Calculator.GetFullSquadDf()  
        user_name= User.query.filter_by(id=current_user.id).first().username
    
        df_display= { 
                    'headings' : FantasyPointsForFullSquad.GetDfHeadingsList(full_squad_df), 
                    'rows' : FantasyPointsForFullSquad.GetDfRowsList(full_squad_df), 
                    'total_points': Fantasy_Calculator.GetTotalFantasyPoints(), 
                    'user_name': user_name
                    } 
        if form.validate_on_submit(): 
            return redirect(url_for('fantasyContest.displayPointsBreakdown', match_id=match_id, user_name=user_name))

        return render_template('fantasyContest/viewFantasyPointSummary.html', df_display=df_display, 
                              form=form) 



@fantasyContest.route('/displayPointsBreakdown', methods=['GET', 'POST'])
def displayPointsBreakdown():   
    match_id = request.args['match_id'] 
    user_name = request.args['user_name']   
    user_id = User.query.filter_by(username=user_name).first().id
    Fantasy_Calculator = __getFantasyCalculatorObject__(match_id=match_id, user_id = user_id)

    batting_df = Fantasy_Calculator.GetBattingDf() 
    bowling_df = Fantasy_Calculator.GetBowlingDf() 
    fielding_df = Fantasy_Calculator.GetFieldingDf()

    df_display= {  
                'user_name': user_name,
                'batting_display' : {
                                    'headings' : FantasyPointsForFullSquad.GetDfHeadingsList(batting_df), 
                                    'rows' : FantasyPointsForFullSquad.GetDfRowsList(batting_df), 
                                    'total_points': Fantasy_Calculator.GetTotalBattingPoints() 
                                    },
                                    
                'bowling_display' : { 
                                    'headings' : FantasyPointsForFullSquad.GetDfHeadingsList(bowling_df), 
                                    'rows' : FantasyPointsForFullSquad.GetDfRowsList(bowling_df), 
                                    'total_points': Fantasy_Calculator.GetTotalBowlingPoints() 
                                    },
                                    

                'fielding_display' : { 
                                    'headings' : FantasyPointsForFullSquad.GetDfHeadingsList(fielding_df), 
                                    'rows' : FantasyPointsForFullSquad.GetDfRowsList(fielding_df), 
                                    'total_points': Fantasy_Calculator.GetTotalFieldingPoints() 
                                    } 
        
                } 

    return render_template('fantasyContest/fantasyPointsBreakdown.html', df_display=df_display) 




def __rankContestants__ (match_id):  
    ## convert the dictionary containing username and fantasy points into a list, 
    ## it would be easier to sort a list
    contestants_records= list(__getAllContestantsRecords__(match_id).values()) 

    ## insert the 0th index for rank, just place 0 for now # [ [0, username, total_fantasy point], [...] ]
    for i in range (len(contestants_records)): 
        contestants_records[i].insert(0,0)


    for i in range (len(contestants_records)-1): 
         for j in range (i+1,len(contestants_records)): 
             if  contestants_records[i][2] <= contestants_records[j][2]: 
                 temp=contestants_records[i]
                 contestants_records[i] = contestants_records[j]
                 contestants_records[j] = temp 
    
    ## put the appropriate ranking now
    for k in range (len(contestants_records)): 
        contestants_records[k][0]=k+1  

    #[ [rank, username, total_fantasy point], [...] ]
    return contestants_records
    




def __getAllContestantsRecords__(match_id): 

    squad_object=SelectedSquad.query.filter_by(match_id=match_id).all()    

    fantasy_points_dict={} 

    ## initialize the dictionary with its keys
    for each in squad_object: 
        fantasy_points_dict[each.user_id]=[None]*2 # will contain [username, total_fantasy_point]
    
    ## place the user names in the dictionary 
    for each_user_id in fantasy_points_dict: 
        fantasy_points_dict[each_user_id][0]=User.query.filter_by(id=each_user_id).first().username  

    ## place the fantasy points in the dictionary 
    for each_user_id in fantasy_points_dict:  
        fantasy_calculator_object = __getFantasyCalculatorObject__(match_id, each_user_id) 
        fantasy_points_dict[each_user_id][1] = fantasy_calculator_object.GetTotalFantasyPoints()


    return fantasy_points_dict




def __getFantasyCalculatorObject__ (match_id, user_id):  

    game_object=GameDetails.query.filter_by(match_id=match_id).first()   
    squad_object=SelectedSquad.query.filter_by(match_id=match_id, 
                                            user_id=user_id).first()   

    #### --------------- Create a fantasy point calculator Object ------------------------######## 
    ''' 
    user_inputs_dict=
    {  
    score_card_url: 'abc.com',  
    squad: [a,b,c],   
    captain:'a', 
    vice_captain: 'b',
    points_per_run: 1, 
    points_per_wicket: 20, 
    } ''' 

    user_inputs_dict={} 
    user_inputs_dict['score_card_url']=game_object.scorecard_link 
    user_inputs_dict['squad']=literal_eval(squad_object.selected_squad)
    user_inputs_dict['captain']=squad_object.captain
    user_inputs_dict['vice_captain']=squad_object.vice_captain 
    user_inputs_dict['points_per_run']=game_object.points_per_run 
    user_inputs_dict['points_per_wicket']=game_object.points_per_wicket
    
    Fantasy_Calculator_Object=FantasyPointsForFullSquad(user_inputs_dict)  

    return Fantasy_Calculator_Object