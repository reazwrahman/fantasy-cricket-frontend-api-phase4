#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 17:07:45 2022

@author: Reaz
"""

import numpy as np 
import pandas as pd

############## Calculate Fantasy Points for Bowling ##################
class FantasyBowlingPoints(object) :
    def __init__(self,score_card,squad,points_per_wicket=20): 
        self.df=score_card 
        self.squad=squad   
        self.points_per_wicket=points_per_wicket
        
    def __GenerateRawDf__(self):  
        bowler_df=self.df
        int_cols = ["Wickets","Runs", "Dots", "Maidens", "Team"]
        for col in int_cols:
            bowler_df[col] = bowler_df[col].astype(int) 
        
    
        bowler_df["base_points"] = self.points_per_wicket*bowler_df["Wickets"]       
        bowler_df["milestone_points"] = bowler_df["Wickets"].replace({1:0, 2:5, 3:15, 4:30, 5:50, 6:50, 7:50, 8:50})        
        bowler_df["bowling_points"] = bowler_df["base_points"] + bowler_df["milestone_points"]
                                                                              
        return bowler_df 
    
    
    def __GenerateFantasyPointsDf__(self): 
        bowler_df=self.__GenerateRawDf__() 
        #print (bowler_df)
        fantasy_df=pd.DataFrame(columns=['Name','base_points','milestone_points','total_points'])
        for i in range (len(bowler_df)):  
            for each_player in self.squad:
                if bowler_df.Name[i] in each_player:  
                    #print (bowler_df.Name[i]) 
                    total_points=bowler_df.base_points[i]+bowler_df.milestone_points[i]
                    fantasy_df=fantasy_df.append(pd.Series([each_player,  
                                                            bowler_df.base_points[i], bowler_df.milestone_points[i], 
                                                            total_points],index=fantasy_df.columns),ignore_index=True) 
        #print (fantasy_df) 
        return fantasy_df 
    
    
    def GetFantasyPointsDf(self): 
        return self.__GenerateFantasyPointsDf__() 
    
    def GetFinalFantasyPoints(self): 
        fantasy_df=self.__GenerateFantasyPointsDf__() 
        return sum(fantasy_df['total_points'])
                

#################### ---------------------------------########################## 



def test():
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/super-smash-2021-22-1289602/central-districts-vs-auckland-14th-match-1289618/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-2nd-test-1288980/full-scorecard'
    
    
    
    ### make me a random squad so i can test ###  
    #from sqg import ListofAllPlayers
    import random 
    from SquadGenerator import ListOfAllPlayers as sqg 
    
    squad_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/match-playing-xi' 
    squads=sqg.AllPlayers(squad_url) 
    full_squad=squads.GetFullSquad() 
    random_squad=[]  
    while len(random_squad)!=11:  
        random_index=random.randrange(len(full_squad)) 
        if full_squad[random_index] not in random_squad:
            random_squad.append(full_squad[random_index]) 
    print (random_squad)
    ##---------------------------------------------- ###
    
    
    ## project includes (only needed for testing)  
    from ScoreCardGenerator import BowlingScoreCardGenerator as scg
    
    scorecard_generator=scg.BowlingScoreCard(score_url) 
    bowling_score_card=scorecard_generator.GetBowlingDf()
    
    c=FantasyBowlingPoints(bowling_score_card, random_squad,points_per_wicket=20)
    cdf= c.GetFantasyPointsDf()
    print (cdf)


if __name__=="__main__": 
    test()
