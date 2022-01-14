#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 15:44:31 2022

@author: Reaz
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np 

############## GET THE DF FOR BATTING SCORE CARD ##################
class BattingScoreCard(object): 
    def __init__(self,URL): 
        self.URL=URL 
    
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
            raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
            
    
    def __GenerateBattingDict__(self): 
        if (BattingScoreCard.ValidateLink(self.URL)):
            page = requests.get(self.URL)
            bs = BeautifulSoup(page.content, 'lxml')
        
            table_body=bs.find_all('tbody')
            batsmen_dict={}
            columns=["Name","Desc","Runs", "Balls", "4s", "6s", "SR", "Team"]
            for i, table in enumerate(table_body[0:len(table_body):2]):
                rows = table.find_all('tr')
                for row in rows[::2]:
                    cols=row.find_all('td')
                    cols=[x.text.strip() for x in cols]
                    if cols[0] == 'Extras':
                        continue
                                              
                    cols[0]=re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip()                     
                    #print (cols)
                    if len(cols) >= len(columns):            
                        name=cols[0]
                        if name not in batsmen_dict:          
                            batsmen_dict[name]={'Desc':cols[1], 'Runs': int(cols[2]),  
                                                'Balls': int(cols[3]),  '4s': int(cols[5]),
                                                '6s': int(cols[6]), #'SR': float(cols[7]),  
                                                'Team': i+1}
                            
                        else:   
                            batsmen_dict[name]['Runs']+= int(cols[2]) 
                            batsmen_dict[name]['Balls']+= int(cols[3])
                            batsmen_dict[name]['4s']+= int(cols[5])  
                            batsmen_dict[name]['6s']+= int(cols[6]) 
                            #batsmen_dict[name]['SR']=(batsmen_dict[name]['Runs']/batsmen_dict[name]['Balls'])*100
                     
                       
        
            return batsmen_dict  
        
        else: 
            raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
            
    
    
    def __ConvertBattingDictToDf__(self): 
        batting_dict=self.__GenerateBattingDict__()  
        batsmen_df = pd.DataFrame(columns=["Name","Desc","Runs", "Balls", "4s", "6s", "Team"])
        for each in batting_dict:  
            batsmen_df=batsmen_df.append(pd.Series([each,batting_dict[each]['Desc'], 
            batting_dict[each]['Runs'],batting_dict[each]['Balls'], batting_dict[each]['4s'],  
            batting_dict[each]['6s'], #batting_dict[each]['SR'], 
            batting_dict[each]['Team']],
            index=batsmen_df.columns), ignore_index=True) 
        
        return batsmen_df
            
            
    
    def GetBattingDict(self): 
        return self.__GenerateBattingDict__() 

    def GetBattingDf(self): 
        return self.__ConvertBattingDictToDf__() 

def test():
    ## live odi
    #score_url='https://www.espncricinfo.com/series/ireland-in-usa-and-west-indies-2021-22-1291182/west-indies-vs-ireland-2nd-odi-1277086/full-scorecard'
    
    ## fully played test match
    score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/full-scorecard' 
    
    ## test with follow on
    #score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-2nd-test-1288980/full-scorecard'
    
    #3 live test 
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-3rd-test-1277081/full-scorecard'
    
    #score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/full-scorecard'

    
    a=BattingScoreCard(score_url) 
    print (a.GetBattingDf()) 

if __name__ =="__main__": 
    test()



        
    
    
            