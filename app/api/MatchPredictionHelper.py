from typing import List, Dict
from ..DynamoAccess import DynamoAccess 

class MatchPredictionHelper(object): 
    def __init__(self, match_id): 
        self.dynamo_access = DynamoAccess()  
        self.match_id = match_id 
        self.teams = self.dynamo_access.GetTeamNames(self.match_id) 
        self.options_dict = None
    
    def GetAllOptions(self) -> Dict[str,str]: 
        options = dict()
        options['team1'] = self.teams[0]+' will win'
        options['team2'] = self.teams[1]+' will win'
        options['draw'] = 'draw/tie'  
        return options 
    
    def GetOptionsDict(self):  
        if self.options_dict == None:  
            self.options_dict = {}
            self.options_dict['team1']=self.teams[0]+' will win' 
            self.options_dict['team2']=self.teams[1]+' will win'  
            self.options_dict['draw']='draw/tie'
        return self.options_dict


