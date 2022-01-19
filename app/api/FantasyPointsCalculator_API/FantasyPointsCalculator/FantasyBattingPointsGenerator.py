#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 16:33:18 2022

@author: Reaz
"""
## python inclues
import numpy as np 
import pandas as pd 


############## Calculate Fantasy Points for Batting ##################
class FantasyBattingPoints(object) :
    def __init__(self,score_card,squad,points_per_run=1): 
        self.df=score_card 
        self.squad=squad  
        self.points_per_run=points_per_run
        
    def __GenerateRawDf__(self): 
        batsmen_df=self.df
        int_cols = ["Runs", "Balls", "4s", "6s", "Team"]
        for col in int_cols:
            batsmen_df[col] = batsmen_df[col].astype(int)
            
        batsmen_df["base_points"] = batsmen_df["Runs"]*self.points_per_run
        batsmen_df["milestone_points"] = (np.floor(batsmen_df["Runs"]/25)).replace(
                                          {1.0:5, 2.0:15, 3.0:30, 4.0:50, 5.0:50, 6.0:50, 7.0:50, 8.0:50})
        batsmen_df["batting_points"] = batsmen_df["base_points"] + batsmen_df["milestone_points"]
                                       
        return batsmen_df 
    
    def __GenerateFantasyPointsDf__(self): 
        batter_df=self.__GenerateRawDf__()
        fantasy_df=pd.DataFrame(columns=['Name','base_points','milestone_points','total_points'])
        for i in range (len(batter_df)):  
            for each_player in self.squad:
                if batter_df.Name[i] in each_player:  
                    #print (batter_df.Name[i]) 
                    total_points=batter_df.base_points[i]+batter_df.milestone_points[i]
                    fantasy_df=fantasy_df.append(pd.Series([each_player,  
                                                            batter_df.base_points[i], batter_df.milestone_points[i], 
                                                            total_points],index=fantasy_df.columns),ignore_index=True) 
        #print (fantasy_df) 
        return (fantasy_df) 
    
    
    def GetFantasyPointsDf(self): 
        return self.__GenerateFantasyPointsDf__() 
    
    def GetFinalFantasyPoints(self): 
        fantasy_df=self.__GenerateFantasyPointsDf__() 
        return sum(fantasy_df['total_points'])
    
        
#################### ---------------------------------##########################


def test():
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    #url='https://www.espncricinfo.com/series/super-smash-2021-22-1289602/central-districts-vs-auckland-14th-match-1289618/full-scorecard'
    score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-2nd-test-1288980/full-scorecard'
    
    
    
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
    from ScoreCardGenerator import BattingScoreCardGenerator as scg
    
    scorecard_generator=scg.BattingScoreCard(score_url) 
    batting_score_card=scorecard_generator.GetBattingDf()
    
    c=FantasyBattingPoints(batting_score_card, random_squad,points_per_run=1)
    cdf= c.GetFantasyPointsDf()
    print (cdf)


if __name__=="__main__": 
    test()

