#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 16:04:15 2022

@author: Reaz
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np 

############## GET THE DF FOR BATTING SCORE CARD ##################
class BowlingScoreCard(object): 
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
            
    
    def __GenerateBowlingDict__(self): 
        if (BowlingScoreCard.ValidateLink(self.URL)):           
            page = requests.get(self.URL)
            bs = BeautifulSoup(page.content, 'lxml')       
            table_body=bs.find_all('tbody')
            
            bowling_dict={}
            columns=['Name', 'Overs', 'Maidens', 'Runs', 'Wickets',
                                      'Econ', 'Dots', '4s', '6s', 'Wd', 'Nb','Team']
            
            for i, table in enumerate(table_body[1:len(table_body):2]):
                rows = table.find_all('tr')
                for row in rows:
                    cols=row.find_all('td')
                    cols=[x.text.strip() for x in cols] 
                    if len(cols)>=len(columns)-1 and len(cols)<=len(columns):
                        name=cols[0] 
                       #print (cols)
                        if name not in bowling_dict:          
                            bowling_dict[name]={'Overs': float(cols[1]), 'Maidens': int(cols[2]),  
                                                'Runs': int(cols[3]),  'Wickets': int(cols[4]),
                                                'Econ': float(cols[5]),'Dots': float(cols[6]), 
                                                '4s': int(cols[7]), '6s': int(cols[8]),
                                                'Wd': int(cols[9]),'Nb': int(cols[10]), 'Team':i+1}

                            
                        else:   
                            bowling_dict[name]['Overs']+=   float(cols[1]) 
                            bowling_dict[name]['Maidens']+= int(cols[2])
                            bowling_dict[name]['Runs']+=    int(cols[3])  
                            bowling_dict[name]['Wickets']+= int(cols[4]) 
                            bowling_dict[name]['Econ']=     bowling_dict[name]['Runs'] / bowling_dict[name]['Overs'] 
                            bowling_dict[name]['Dots']+=    int(cols[6])
                            bowling_dict[name]['4s']+=      int(cols[7])  
                            bowling_dict[name]['6s']+=      int(cols[8])  
                            bowling_dict[name]['Wd']+=      int(cols[9])  
                            bowling_dict[name]['Nb']+=      int(cols[9])
            
            return bowling_dict
        
        else: 
            raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
            
    
    
    def __ConvertBowlingDictToDf__(self):        
        bowling_dict=self.__GenerateBowlingDict__()  
        bowling_df = pd.DataFrame(columns=['Name', 'Overs', 'Maidens', 'Runs', 'Wickets',
                                  'Econ', 'Dots', '4s', '6s', 'Wd', 'Nb','Team'])
        for each in bowling_dict:  
            bowling_df=bowling_df.append(pd.Series([each,bowling_dict[each]['Overs'], 
            bowling_dict[each]['Maidens'],bowling_dict[each]['Runs'], bowling_dict[each]['Wickets'],  
            bowling_dict[each]['Econ'], bowling_dict[each]['Dots'],bowling_dict[each]['4s'], 
            bowling_dict[each]['6s'], bowling_dict[each]['Wd'], bowling_dict[each]['Nb'], 
            bowling_dict[each]['Team']],
            index=bowling_df.columns), ignore_index=True) 
        
        return bowling_df
            
    
    def GetBowlingDict(self): 
        return self.__GenerateBowlingDict__() 

    def GetBowlingDf(self): 
        return self.__ConvertBowlingDictToDf__()  
    
def test():
    ## live odi
    #score_url='https://www.espncricinfo.com/series/ireland-in-usa-and-west-indies-2021-22-1291182/west-indies-vs-ireland-2nd-odi-1277086/full-scorecard'
    
    ## fully played test match
    score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/full-scorecard' 
    
    ## test with follow on
    #score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-2nd-test-1288980/full-scorecard'
    
    #3 live test 
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-3rd-test-1277081/full-scorecard'
    
    a=BowlingScoreCard(score_url) 
    print (a.GetBowlingDf()) 
    
if __name__ =="__main__": 
    test()

