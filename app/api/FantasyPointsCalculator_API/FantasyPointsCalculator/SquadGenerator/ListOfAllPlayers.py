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

class AllPlayers(object): 
    
    def __init__(self,url): 
        self.URL=url   
        self.raw_data=[]
        self.team1Squad,self.team2Squad=self.__PrepareTeams__() 
        
    
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
                team1.append(each[1]) 
                team2.append(each[2])   
        
        return team1,team2
        

    def GetTeam1Squad(self):  
        #print (self.team2Squad) #for debugging
        return self.team1Squad
    
    def GetTeam2Squad(self):  
        #print (self.team2Squad) # for debugging
        return self.team2Squad
    
    def GetFullSquad(self): 
        full_squad=self.team1Squad + self.team2Squad
        return full_squad  
    
    # includes batting allrounders
    def GetAllBatters(self): 
        batters=[] 
        full_squad=self.GetFullSquad() 
        for each in full_squad: 
            if 'bat' in each: 
                batters.append(each)  
                
        
        return batters
    
    # includes bowling allrounders
    def GetAllBowlers(self): 
        bowlers=[] 
        full_squad=self.GetFullSquad() 
        for each in full_squad: 
            if 'bowl' in each: 
                bowlers.append(each)  
                
        ## find the pure allrounders (like Ben Stokes) and put them into bowlers for now  
        batters=self.GetAllBatters() 
        combined=batters+bowlers 
        for each in full_squad: 
            if each not in combined and len(each)>1: 
                bowlers.append(each)
                
        return bowlers
    
    def GetAllAllRounders(self): 
        allRounders=[] 
        full_squad=self.GetFullSquad() 
        for each in full_squad: 
            if 'allrounder' in each: 
                allRounders.append(each) 
        return allRounders 

    def GetAllWicketKeepers(self): 
        keepers=[] 
        full_squad=self.GetFullSquad() 
        for each in full_squad: 
            if 'wicket' in each: 
                keepers.append(each) 
        return keepers 
    
        
def test():
    #URL='https://www.espncricinfo.com/series/the-ashes-2021-22-1263452/australia-vs-england-3rd-test-1263464/match-squads'
    URL='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/match-squads'
    a=AllPlayers(URL) 
    #print (a.GetFullSquad()) 
    #print (a.GetAllBatters()) 
    print(a.GetAllBowlers()) 
    #print(a.GetAllAllRounders())  
    #print(a.GetAllWicketKeepers()) 

if __name__=="__main__": 
    test()
