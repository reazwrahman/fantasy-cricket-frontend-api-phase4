import os,sys 
import boto3  
import simplejson as json
from decimal import Decimal 
from boto3.dynamodb.conditions import Key 

from .models import GameDetails


''' 
Responsible for handling all dynamo related calls  
'''

class DynamoAccess(object): 
    def __init__(self): 
        self.dynamodb = boto3.resource('dynamodb')   
        self.table_name = 'all_match_info'
        self.table = self.dynamodb.Table(self.table_name)  

    
    def AddGameDetails(self, game_details:GameDetails): 
        game_info_dict = {'squad_link': game_details.squad_link, 
                          'game_start_time': game_details.game_start_time 
                        } 
        
        item = {'match_id': game_details.match_id, 
                'game_status': game_details.game_status, 
                'game_details': game_info_dict
                } 
        
        response = self.table.put_item(Item = item) 
        print (response) 
        return 