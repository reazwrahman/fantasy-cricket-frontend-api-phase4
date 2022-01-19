#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 17:16:23 2022

@author: Reaz
"""

import re 
import pandas as pd

############## Calculate Fantasy Points for Fielding ##################
class FantasyFieldingPoints(object) :
    def __init__(self,batting_score_card,squad,points_per_catch=10): 
        self.batsmen_df=batting_score_card 
        self.squad=squad  
        self.points_per_catch=points_per_catch
        
    def __GenerateRawDf__(self): 
        fielders = []
        for wicket in self.batsmen_df["Desc"]:
            if wicket.find("c & b") == 0:
                fielders.append(wicket.split("c & b")[1].strip())
            elif wicket.find("c") == 0:
                fielders.append(wicket.split("c ")[1].split("b ")[0].strip())
            if wicket.find("st") == 0:
                fielders.append(wicket.split("st ")[1].split("b ")[0].strip())
            if wicket.find("run out") == 0:
                fielders.extend([x.strip() for x in wicket.split("run out")[1].replace('(', '').replace(')', '').split("/")])
            if wicket.find("sub (") != -1:
                del fielders[-1]
        #print (f' fielders= {fielders}') # for debugging
        fielders = [re.sub(r"\W+", ' ', fielder).strip() for fielder in fielders]          
        #print (f' fielders2 = {fielders}') # for debugging
        
        ## store the fielders dismissals result into a dictionary
        point_dict={} 
        for each in fielders: 
            if each not in point_dict: 
                point_dict[each]=1 
            else: 
                point_dict[each]+=1 
        
        ## convert the points dict dictionary into a df
        fielder_df = pd.DataFrame(columns=['Name','Dismissals','total_points'])  
        for each in point_dict: 
            fielder_df=fielder_df.append(pd.Series([each,point_dict[each], point_dict[each]*self.points_per_catch], 
                                                   index=fielder_df.columns),ignore_index=True) 
        
        return fielder_df
    
    def __GenerateFantasyPointsDf__(self): 
        fielder_df=self.__GenerateRawDf__()
        fantasy_df=pd.DataFrame(columns=['Name','base_points','milestone_points','total_points'])
        for i in range (len(fielder_df)):  
            for each_player in self.squad:
                if fielder_df.Name[i] in each_player:  
                    #print (bowler_df.Name[i]) 
                    total_points=fielder_df.total_points[i]
                    fantasy_df=fantasy_df.append(pd.Series([each_player,  
                                                            fielder_df.total_points[i], 0.0, 
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
    from ScoreCardGenerator import FieldingScoreCardGenerator as scg
    
    scorecard_generator=scg.FieldingScoreCard(score_url) 
    fielding_score_card=scorecard_generator.GetFieldingDf()
    
    c=FantasyFieldingPoints(fielding_score_card, random_squad,points_per_catch=10)
    cdf= c.GetFantasyPointsDf()
    print (cdf)


if __name__=="__main__": 
    test()
