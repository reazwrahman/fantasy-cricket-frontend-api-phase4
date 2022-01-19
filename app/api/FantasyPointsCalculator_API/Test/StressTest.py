#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 11:08:29 2022

@author: Reaz
"""

import sys
import os  
import random

# project includes 
from TestCases import TestDict
  
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
  
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
  
# adding the parent directory to 
# the sys.path.
sys.path.append(parent) 

import FantasyPointsCalculatorIF    
from FantasyPointsCalculator.SquadGenerator.ListOfAllPlayers import AllPlayers


def stress_test():
    for each in TestDict:  
        squad_url=TestDict[each]['squad_url']
        score_url=TestDict[each]['score_url']
    
    
        try: 
            # =============================================================================
            squads=AllPlayers(squad_url) 
            full_squad=squads.GetFullSquad() 
            random_squad=[]  
            while len(random_squad)!=11:  
                random_index=random.randrange(len(full_squad)) 
                if full_squad[random_index] not in random_squad:
                    random_squad.append(full_squad[random_index])
            # ============================================================================= 
            
            user_inputs_dict={ 
              'score_card_url': score_url,  
              'squad': random_squad,   
              'captain':random_squad[0], 
              'vice_captain': random_squad[1],
              'points_per_run': 1, 
              'points_per_wicket': 20, 
              }   
            
            test = FantasyPointsCalculatorIF.FantasyPointsForFullSquad(user_inputs_dict) 
            test.GetBattingDf()
            test.GetTotalBattingPoints()
            
            test.GetBowlingDf()
            test.GetTotalBowlingPoints()
            
            test.GetFieldingDf()
            test.GetTotalFieldingPoints()
                     
            test.GetFullSquadDf()
            test.GetTotalFantasyPoints() 
            
            print (f'PASSED FOR {each}')
        
        except:  
            print ('# =============================================================================')
            print (f'Stess Test Failed for {each}') 
            print (f'Squad_URL: {squad_url}') 
            print (f'Score_URL: {score_url}')


if __name__ =="__main__": 
    stress_test()
  
