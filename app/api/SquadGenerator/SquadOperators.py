from typing import List, Dict

''' performs different 
operations on a given squad dictionary'''
class SquadOperators(object): 
    def __init__(self, match_squad): 
        self.full_squad_dict = match_squad 
    

    def GetAllBatters(self): 
        return self.__filterByRole__('batter')
    
    # includes bowling allrounders
    def GetAllBowlers(self): 
        return self.__filterByRole__('bowler') 
                
    
    def GetAllAllRounders(self): 
        return self.__filterByRole__('allrounder')  

    def GetAllWicketKeepers(self): 
        return self.__filterByRole__('wicketkeeper') 

    def __filterByRole__(self, role:str): 
        filtered_dict = {} 
        for each in self.full_squad_dict: 
            all_roles = self.full_squad_dict[each]['Role'] 
            if role in all_roles: 
                filtered_dict[each] = self.full_squad_dict[each] 
        
        return filtered_dict

    def UpdateSquadKeys(self, old_squad, new_squad):  
       pass


    def GetNonOverlappingPlayers(self, primary_dict): 
        secondary_dict = {} 
        for each in self.full_squad_dict: 
            if each not in primary_dict : 
                secondary_dict[each] = self.full_squad_dict[each] 
        
        return secondary_dict 

    def GetPlayerNamesFromDict(self, player_dict) ->List[str] :
        names = [] 
        for each in player_dict: 
            names.append(player_dict[each]['Name']) 
        
        return names 
    
    ## key = playername, value = playerid
    def GetReversedDict(self, player_dict): 
        reversed_dict = {} 
        for each in player_dict: 
            player_id = each 
            player_name = player_dict[each]['Name'] 
            reversed_dict[player_name] = player_id

        return reversed_dict     
    
    def GetNamesListFromIds(self, player_id:List, match_squad_dict:Dict): 
        names = []  
        for each in player_id: 
            names.append(match_squad_dict[each]['Name']) 
        return names 
    
    def AddPlayingXiIndicator(self, playing_xi_dict): 
        match_squad_reversed_dict = self.GetReversedDict(self.full_squad_dict) 
        for each in playing_xi_dict: 
            player_name = playing_xi_dict[each]['Name'] 
            if player_name in match_squad_reversed_dict: 
                original_player_id = match_squad_reversed_dict[player_name]
                self.full_squad_dict[original_player_id]['InPlayingXi'] = True 
        
        return self.full_squad_dict 
    

    def AttachPlayingXiTagToNames(self, list_of_names:List[str], match_squad_dict:Dict) -> List[str]: 
        match_squad_reversed_dict = self.GetReversedDict(match_squad_dict)  
        for i in range(len(list_of_names)): 
            player_name = list_of_names[i]
            player_id = match_squad_reversed_dict[player_name] 
            playing_xi_status = match_squad_dict[player_id]['InPlayingXi'] 
            if playing_xi_status:  
                list_of_names[i] = list_of_names[i] + ' [In Playing XI]'
        
        return list_of_names 
    
    def RemovePlayingXiTagFromName(self, player_name):  
        if ' [In Playing XI]' in player_name:  
            player_name = player_name.replace(' [In Playing XI]', '')
        return player_name




