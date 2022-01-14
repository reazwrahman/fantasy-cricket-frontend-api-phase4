#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 11:04:29 2022

@author: Reaz
"""

#python includes 
import pandas as pd


## Project Includes 
try: ## for outside of flask project usecases
    from FantasyPointsCalculator.ScoreCardGenerator.BattingScoreCardGenerator import BattingScoreCard 
    from FantasyPointsCalculator.ScoreCardGenerator.BowlingScoreCardGenerator import BowlingScoreCard 
    from FantasyPointsCalculator.ScoreCardGenerator.FieldingScoreCardGenerator import FieldingScoreCard

    from FantasyPointsCalculator.FantasyBattingPointsGenerator import FantasyBattingPoints 
    from FantasyPointsCalculator.FantasyBowlingPointsGenerator import FantasyBowlingPoints
    from FantasyPointsCalculator.FantasyFieldingPointsGenerator import FantasyFieldingPoints

except ModuleNotFoundError: ## for inside of flask project environemnt 
    from .FantasyPointsCalculator.ScoreCardGenerator.BattingScoreCardGenerator import BattingScoreCard 
    from .FantasyPointsCalculator.ScoreCardGenerator.BowlingScoreCardGenerator import BowlingScoreCard 
    from .FantasyPointsCalculator.ScoreCardGenerator.FieldingScoreCardGenerator import FieldingScoreCard

    from .FantasyPointsCalculator.FantasyBattingPointsGenerator import FantasyBattingPoints 
    from .FantasyPointsCalculator.FantasyBowlingPointsGenerator import FantasyBowlingPoints
    from .FantasyPointsCalculator.FantasyFieldingPointsGenerator import FantasyFieldingPoints

''' 
user_inputs_dict=
{  
 score_card_url: 'abc.com',  
 squad: [a,b,c],   
 captain:'a', 
 vice_captain: 'b',
 points_per_run: 1, 
 points_per_wicket: 20, 
 }  

output format: 
    Name    Batting     Bowling     Fielding    Cap_Vc  Total
    
    on the website we can display batting, bowling and fielding dfs separately as well, with view details breakdown button
'''
class FantasyPointsForFullSquad(object): 
    def __init__(self,user_inputs_dict): 
        self.parameters_dict=user_inputs_dict  
        
        ## get all the scorecards
        self.batting_scorecard=BattingScoreCard(self.parameters_dict['score_card_url'])
        self.bowling_scorecard=BowlingScoreCard(self.parameters_dict['score_card_url']) 
        self.fielding_scorecard=FieldingScoreCard(self.parameters_dict['score_card_url']) 
        
        ## calculate all the fantasy points
        self.batting_object=FantasyBattingPoints(self.batting_scorecard.GetBattingDf(),  
                                                    self.parameters_dict['squad'], 
                                                    points_per_run=self.parameters_dict['points_per_run']) 
        
        self.bowling_object=FantasyBowlingPoints(self.bowling_scorecard.GetBowlingDf(),  
                                                    self.parameters_dict['squad'], 
                                                    points_per_wicket=self.parameters_dict['points_per_wicket'])
        
        
        self.fielding_object=FantasyFieldingPoints(self.fielding_scorecard.GetFieldingDf(),  
                                                    self.parameters_dict['squad'])
        
    
    def GetBattingDf(self):  
        return self.batting_object.__GenerateFantasyPointsDf__() 

    def GetTotalBattingPoints(self): 
        return self.batting_object.GetFinalFantasyPoints() 
    
    
    
    def GetBowlingDf(self):  
        return self.bowling_object.__GenerateFantasyPointsDf__() 

    def GetTotalBowlingPoints(self): 
        return self.bowling_object.GetFinalFantasyPoints()   
    
    
    
    def GetFieldingDf(self):  
        return self.fielding_object.__GenerateFantasyPointsDf__() 

    def GetTotalFieldingPoints(self): 
        return self.fielding_object.GetFinalFantasyPoints()  
    
    
    def __ApplyCapVcPoints__(self,final_dict): 
        for each in final_dict: 
            if each in self.parameters_dict['captain']: 
                final_dict[each]['Cap_Vc']=final_dict[each]['Total'] 
                final_dict[each]['Total']*=2  
                captain=each

                
            if each in self.parameters_dict['vice_captain']: 
                final_dict[each]['Cap_Vc']=final_dict[each]['Total']/2 
                final_dict[each]['Total']*=1.5  
                vice_captain=each 
          
        
        ## change the keys to reflect he is the fantasy captain 
        final_dict[f'{captain} [captain]']=final_dict[captain] 
        del(final_dict[captain]) 
        ## change the keys to reflect he is the fantasy vice captain 
        final_dict[f'{vice_captain} [vc]']=final_dict[vice_captain] 
        del(final_dict[vice_captain])

        return final_dict 
    
    
    def __AddZeroPointsPlayers__(self,final_dict):    
        contribution_areas= list(final_dict[list(final_dict.keys())[0]].keys()) ## get all the keys of the first dictionary entry namely batting, bowling, fielding etc.
        for each in self.parameters_dict['squad']: 
            if each not in final_dict:  
                final_dict[each]={}
                for each_key in list(contribution_areas): 
                    final_dict[each][each_key]=0.0 
        return final_dict
        
    
    def GetFullSquadDict(self): 
        batting=self.batting_object.__GenerateFantasyPointsDf__() 
        bowling=self.bowling_object.__GenerateFantasyPointsDf__()  
        fielding=self.fielding_object.__GenerateFantasyPointsDf__()   
        
        all_dfs=[batting,bowling,fielding]
        df_keys=['Batting','Bowling','Fielding','Cap_Vc']
        
        final_dict={} 
        
        for i in range (len(all_dfs)):
            for j in range (len(all_dfs[i])):  
                if all_dfs[i].Name[j] not in final_dict: 
                    final_dict[all_dfs[i].Name[j]]={} 
                
                for k in range (len(df_keys)):  
                    if k == i: 
                        final_dict[all_dfs[i].Name[j]][df_keys[k]]=all_dfs[i].total_points[j] 
                    else: 
                        if df_keys[k] not in final_dict[all_dfs[i].Name[j]]: 
                            final_dict[all_dfs[i].Name[j]][df_keys[k]]=0.0
        
              
        for each in final_dict: 
            final_dict[each]['Total']=sum([final_dict[each]['Batting'], 
                                    final_dict[each]['Bowling'], 
                                    final_dict[each]['Fielding'], 
                                    final_dict[each]['Cap_Vc']])
                    
        
        ## add all the non contributing players as 0 points
        final_dict=self.__AddZeroPointsPlayers__(final_dict)
        
        ## APPLY CAP_VC POINTS 
        final_dict=self.__ApplyCapVcPoints__(final_dict) 
        

        return final_dict  
    
    
    def GetFullSquadDf(self): 
        final_dict=self.GetFullSquadDict() 
        final_df=pd.DataFrame(columns=['Name','Batting','Bowling','Fielding','Cap_Vc','Total']) 
        
        for each in final_dict:      
            final_df=final_df.append(pd.Series([each,
                                                final_dict[each]['Batting'], final_dict[each]['Bowling'], 
                                                final_dict[each]['Fielding'], final_dict[each]['Cap_Vc'],
                                                final_dict[each]['Total']],index=final_df.columns),ignore_index=True) 
    
      
        return final_df 
    
    
    def GetTotalFantasyPoints(self): 
        return sum(self.GetFullSquadDf()['Total']) 
    
    
    @staticmethod 
    def GetDfHeadingsList(df): 
        return (list(df.columns)) 
    
    @staticmethod 
    def GetDfRowsList(df): 
        rows=[]
        for i in range(len(df)): 
            rows.append(list(df.loc[i]))
        return rows
              
def test():    
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/super-smash-2021-22-1289602/central-districts-vs-auckland-14th-match-1289618/full-scorecard'
    
    
    ### make me a random squad so i can test ###  
    from FantasyPointsCalculator.SquadGenerator.ListOfAllPlayers import AllPlayers 
    import random
    #squad_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/match-playing-xi' 
    squad_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/match-squads'
    
    # squads=AllPlayers(squad_url) 
    # full_squad=squads.GetFullSquad() 
    # random_squad=[]  
    # while len(random_squad)!=11:  
    #     random_index=random.randrange(len(full_squad)) 
    #     if full_squad[random_index] not in random_squad:
    #         random_squad.append(full_squad[random_index])
            
    
    random_squad=['Devon Conway top-order batter', 'Henry Nicholls top-order batter', 'Ross Taylor middle-order batter', 'Mahmudul Hasan Joy top-order batter', 'Najmul Hossain Shanto top-order batter', 'Shadman Islam opening batter', 'Trent Boult bowler', 'Tim Southee bowler', 'Neil Wagner bowler', 'Shoriful Islam bowler', 'Mehidy Hasan Miraz allrounder']
    
    user_inputs_dict={ 
      'score_card_url': score_url,  
      'squad': random_squad,   
      'captain':random_squad[0], 
      'vice_captain': random_squad[1],
      'points_per_run': 1, 
      'points_per_wicket': 20, 
      }   
    
    test=FantasyPointsForFullSquad(user_inputs_dict) 
    print (test.GetBattingDf())
    print (test.GetTotalBattingPoints()) 
    print ('---------------------')
    print (test.GetBowlingDf())
    print (test.GetTotalBowlingPoints()) 
    print ('---------------------')
    print (test.GetFieldingDf())
    print (test.GetTotalFieldingPoints()) 
    
    print ('------------------') 
    print (test.GetFullSquadDf()) 
    print(test.GetTotalFantasyPoints()) 

if __name__=="__main__": 
    test()