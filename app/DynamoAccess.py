from typing import Dict
import os,sys 
import boto3  
import simplejson as json
from decimal import Decimal 
from boto3.dynamodb.conditions import Key, Attr 

from .models import GameDetails


''' 
Responsible for handling all dynamo related calls  
'''

class DynamoAccess(object): 
    def __init__(self): 
        self.dynamodb = boto3.resource('dynamodb')   
        self.table_name = 'all_match_info'
        self.table = self.dynamodb.Table(self.table_name)  

    
    def CreateNewGame(self, game_details:GameDetails): 
        game_info_dict = {'game_title': game_details.game_title,
                          'squad_link': game_details.squad_link, 
                          'game_start_time': game_details.game_start_time 
                        } 
        
        dynamo_item = {'match_id': game_details.match_id, 
                'game_status': game_details.game_status, 
                'game_details': game_info_dict
                } 
        
        response = self.table.put_item(Item = dynamo_item) 
        print (response) 
        return  
    
    def GetActiveGamesByIdAndTitle(self): 
        response = self.table.scan(
                    FilterExpression=Attr("game_status").eq('Active')
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        active_games = [] 
        for each in json_list: 
            active_games.append((each['match_id'], each['game_details']['game_title']))  
        return active_games 

    def AddScoreCardDetails(self, match_id:str, scorecard_details:Dict): 
        update_expression=  "set scorecard_details=:scorecard_details"   
        try:
            response = self.table.update_item( 
                Key={'match_id': match_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':scorecard_details': json.loads(json.dumps(scorecard_details), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )   
            return True 
        except: 
            return False
         
    
    def GetGameTitle(self, match_id:str): 
        response = self.table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'game_details')  
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True)) 
        return json_list[0]['game_details']['game_title']

