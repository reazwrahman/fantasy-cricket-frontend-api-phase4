#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 17:25:22 2022

@author: Reaz
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np 

############## GET THE DF FOR BATTING SCORE CARD ##################
class FieldingScoreCard(object): 
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
            
    
    def __GenerateFieldingDf__(self): 
        if (FieldingScoreCard.ValidateLink(self.URL)):
            page = requests.get(self.URL)
            bs = BeautifulSoup(page.content, 'lxml')
        
            table_body=bs.find_all('tbody')
            fielding_df = pd.DataFrame(columns=["Name","Desc","Team"]) 
            batting_columns=["Name","Desc","Runs", "Balls", "4s", "6s", "SR", "Team"]
            
            for i, table in enumerate(table_body[0:len(table_body):2]):
                rows = table.find_all('tr')
                for row in rows[::1]:
                    cols=row.find_all('td')
                    cols=[x.text.strip() for x in cols]
                    if cols[0] == 'Extras':
                        continue
                                              
                    cols[0]=re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip()                     
                    #print (cols)
                    if len(cols) >= len(batting_columns):            
                        fielding_df = fielding_df.append(pd.Series(
                        [re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), cols[1],i+1], 
                        index=fielding_df.columns ), ignore_index=True)
                     
                            
            return fielding_df 
        
        else: 
            raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
            
    
    
    def __ConvertFieldingDictToDf__(self): 
        pass
            
            
    
    def GetFieldingDict(self): 
        pass

    def GetFieldingDf(self): 
        return self.__GenerateFieldingDf__()  
    
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
    
    
    a=FieldingScoreCard(score_url) 
    print (a.GetFieldingDf())     

if __name__ == "__main__": 
    test()        
    
    
    
    
    
    
