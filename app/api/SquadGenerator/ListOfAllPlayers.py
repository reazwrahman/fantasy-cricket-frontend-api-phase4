#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 18:05:35 2021

@author: Reaz
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np 
from typing import List, Dict

class AllPlayers(object): 
    
    ''' we can either pass the full squad dict from the database 
        to utilize the helper functions in this class, 
        or we can just create the full squad dict for the first time 
        by not passing in the optional parameter BUT by passing in the url
    '''
    def __init__(self,url=None, full_squad_dict = None):     
        if full_squad_dict:   
             self.full_squad_dict = full_squad_dict 
        elif url:   
            self.raw_data=[] 
            self.URL=url 
            self.team1Squad,self.team2Squad=self.__PrepareTeams__() 
            self.full_squad_dict = self.MakeFullSquadDict()  
        else: 
            raise ValueError('AllPlayers constructor needs either match squad or a squad link, invalid parameters provided')

        
    
    @staticmethod 
    def ValidateLink(URL): 
        try: 
            page = requests.get(URL)
            bs = BeautifulSoup(page.content, 'lxml')  
            
            table_body=None
            table_body=bs.find_all('tbody') 
            
            if table_body == None: 
                return False 
            else: 
                return True
            
        except: 
            raise Exception('AllPlayers::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' )
        
        
    def __PrepareRawData__(self): 
       
        if (AllPlayers.ValidateLink(self.URL)):           
            raw_data=[]            
            page = requests.get(self.URL)
            bs = BeautifulSoup(page.content, 'lxml') 
            
            ## put player information into a list  
            table_body=bs.find_all('tbody')
            batsmen_df = pd.DataFrame(columns=["Name","Desc","Runs", "Balls", "4s", "6s", "SR", "Team"])
            for i, table in enumerate(table_body[0:4:2]):
                rows = table.find_all('tr')
                for row in rows:
                    cols=row.find_all('td')
                    cols=[x.text.strip() for x in cols]   
                    if cols[0] == 'Bench':  ## useful when the playing xi is out
                        break 
                        break 
                    raw_data.append(cols)  
            
            return raw_data 
    
        else: 
            raise Exception('AllPlayers::__PrepareRawData__(), Could not generate squads, link validation failed' )
            

    
    def __PrepareTeams__(self):  
        self.raw_data=self.__PrepareRawData__()
        team1=[] 
        team2=[] 
        for each in self.raw_data:  
            if len(each) == 3: 
                ## to wipe out the '-' player 
                if len(each[1]) > 1:
                    team1.append(each[1])  
                if len(each[2]) > 1:
                    team2.append(each[2])   
        
        return team1,team2
        

    def GetTeam1Squad(self):  
        #print (self.team2Squad) #for debugging
        return self.team1Squad
    
    def GetTeam2Squad(self):  
        #print (self.team2Squad) # for debugging
        return self.team2Squad
    
    def MakeFullSquadDict(self):  
        self.team1Squad,self.team2Squad=self.__PrepareTeams__()
        full_squad_list=self.team1Squad + self.team2Squad  
        self.full_squad_dict = {}
        for i in range (len(full_squad_list)): 
            self.full_squad_dict[i+1] = {}
            self.full_squad_dict[i+1]['Name'] = full_squad_list[i] 
            self.full_squad_dict[i+1]['Role'] = []

        self.__AddPlayerRoles__()
        return self.full_squad_dict    

    def __AddPlayerRoles__(self): 
        for each in self.full_squad_dict:
            name = self.full_squad_dict[each]['Name'] 

            has_defined_role = False
            if 'bat' in name:  
                self.full_squad_dict[each]['Role'].append('batter')  
                has_defined_role = True
            if 'bowl' in name: 
                self.full_squad_dict[each]['Role'].append('bowler')    
                has_defined_role = True          
            if 'allrounder' in name: 
                self.full_squad_dict[each]['Role'].append('allrounder') 
                has_defined_role = True 
            if 'wicket' in name: 
                self.full_squad_dict[each]['Role'].append('wicketkeeper')  
                has_defined_role = True
            
            if not has_defined_role:
                self.full_squad_dict[each]['Role'].append('other')

    def GetFullSquad(self):  
        return self.full_squad_dict 
    
 
    def UpdateSquadKeys(self, old_squad, new_squad):  
        ''' 
        context: with the playing xi link, we will get new keys for each player 
        if someone submits a squad before playing xi link, the keys will point to wrong players 
        therefore, we need to retain the old keys into the new squad
    '''  
        # get the max key value from the old_squad 
        max_key = 0 
        for each in old_squad: 
            if each >= max_key: 
                max_key = each  
        
        updated_dict = {} 
        for each in new_squad: 
            

        
    


    
    # includes batting allrounders
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

    def GetNonOverlappingPlayers(self, primary_dict): 
        secondary_dict = {} 
        for each in self.full_squad_dict: 
            if each not in primary_dict : 
                secondary_dict[each] = self.full_squad_dict[each] 
        
        return secondary_dict 

    def GetPlayerNamesFromDict(self, player_dict): 
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

        
def test():
    #URL='https://www.espncricinfo.com/series/the-ashes-2021-22-1263452/australia-vs-england-3rd-test-1263464/match-squads'
    URL='https://www.espncricinfo.com/series/australia-in-india-2022-23-1348637/india-vs-australia-2nd-test-1348653/match-playing-xi'
    a=AllPlayers(URL) 
    #print (a.GetFullSquad()) 
    print (a.GetAllBatters())  
    print ('---------------')
    #print(a.GetAllBowlers())  
    #print ('---------------')
    #print(a.GetAllAllRounders())  
    #print ('---------------') 
    #print(a.GetAllWicketKeepers())  
    print (a.GetNonOverlappingPlayers(a.GetAllBatters()))

if __name__=="__main__": 
    test()
