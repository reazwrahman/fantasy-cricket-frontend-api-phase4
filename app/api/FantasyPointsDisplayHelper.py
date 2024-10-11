from typing import List, Dict 
from datetime import datetime
import pytz 
import json

''' 
used by frontend to create display dataframes 
'''
class FantasyPointsDisplayHelper(object): 
    def __init__(self): 
        pass   

    def convertRankingToDict(self, fantasy_data:list) -> dict: 
        rankings = [
            {
                "rank": entry[0],
                "name": entry[1],
                "score": entry[2],
                "id": entry[3]
            }
            for entry in fantasy_data
        ]

        # Create the final JSON structure
        result = {"rankings": rankings}
    
        # Convert the result to Dictionary format
        return result

    def GetTimeDeltaMessage(self, last_updated_time): 

        input_time_naive = datetime.strptime(last_updated_time, '%Y-%m-%d %H:%M:%S %Z')
        input_time = pytz.utc.localize(input_time_naive)
        current_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        time_diff_minutes = int((current_time - input_time).total_seconds() / 60)

        if time_diff_minutes == 0: 
            return "Last Updated on less than 1 minute ago"  
        elif time_diff_minutes == 1: 
            return "Last Updated on 1 minute ago"  
        elif time_diff_minutes > 59: 
            return "Last Updated on more than 1 hour ago" 
        else: 
            return f"Last Updated on {time_diff_minutes} minutes ago"

    def HideUserIdFromRanking(self, fantasy_ranking): 
        for i in range (len(fantasy_ranking)): 
            fantasy_ranking[i].pop() 
        
        return fantasy_ranking
    
    def AddMedalsToRanking(self, fantasy_ranking:dict) ->dict:               
                    ## BRONZE, SILVER, GOLD EMOJI 
        ranking = fantasy_ranking["rankings"]
        medals = [u"\U0001F949", u"\U0001F948", u"\U0001F947"]
        i = 0 
        while i < len(ranking) and len(medals) > 0:
            curr_medal = medals.pop() 
            ranking[i]['medal'] = curr_medal 
            i+=1 
        
        return fantasy_ranking


    def GetSummaryPointsHeader(self): 
        return ['Name','Batting','Bowling','Fielding','Cap/VC','Total']  

    def GetBreakdownPointsHeader(self): 
        return ['Name','Base Points', 'Milestone Points', 'Total Points']

    def CreateSummaryPointsDisplay(self, summary_points:Dict, squad_selection:Dict) -> List:  
        '''['Name','Batting','Bowling','Fielding','Cap/VC','Total'] '''

        selected_squad = squad_selection['selected_squad'] 
        captain_id = squad_selection['captain'] 
        vc_id = squad_selection['vice_captain']

        display_list = []    
        total_points = 0

        for each_id in selected_squad:  
            if each_id in summary_points: 
                local_list = [summary_points[each_id]['Name'], summary_points[each_id]['Batting'], 
                                   summary_points[each_id]['Bowling'], summary_points[each_id]['Fielding'], 
                                   0, summary_points[each_id]['Total']] 

                if each_id == captain_id:  
                    local_list[0] += ' [Captain]'
                    local_list[4] = local_list[5] 
                    local_list[5] *=2 
                elif each_id == vc_id:  
                    local_list[0] += ' [Vice Captain]'
                    local_list[4] = local_list[5]/2 
                    local_list[5] *= 1.5
         
            total_points += local_list[-1]
            display_list.append(local_list) 
        
        return [display_list, total_points] 
    


    def CreateBreakdownPointsDisplay(self, breakdown_points:Dict, squad_selection:Dict) -> List:  
        ''' ['Name','Batting','Bowling','Fielding','Cap/VC','Total'] '''
        selected_squad = squad_selection['selected_squad'] 
        captain_id = squad_selection['captain'] 
        vc_id = squad_selection['vice_captain']

        display_list = []    
        total_points = 0  

        for each_id in selected_squad:  
            if each_id in breakdown_points: 
                local_list = [breakdown_points[each_id]['Name'], breakdown_points[each_id]['base_points'], 
                              breakdown_points[each_id]['milestone_points'], breakdown_points[each_id]['total_points']]  
                
                total_points += local_list[-1] 
                display_list.append(local_list) 
        
        return [display_list, total_points]

                


