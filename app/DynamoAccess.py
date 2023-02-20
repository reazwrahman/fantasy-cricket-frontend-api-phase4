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
        self.match_info_table_name = 'all_match_info' 
        self.match_table = self.dynamodb.Table(self.match_info_table_name)   

        self.selected_squads_table_name = 'selected_squads'
        self.squad_table = self.dynamodb.Table(self.selected_squads_table_name)


    ''' ------------------------------------ COMMON QUERIES ------------------------------------ ''' 
    def GetActiveGamesByIdAndTitle(self): 
        response = self.match_table.scan(
                    FilterExpression=Attr("game_status").eq('Active')
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        active_games = [] 
        for each in json_list: 
            active_games.append((each['match_id'], each['game_title']))  
        return active_games  
    
    
    def GetGameTitle(self, match_id:str): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'game_title')  
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True)) 
        return json_list[0]['game_title']  
    
    def GetGameStartTime(self, match_id): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'game_start_time')  
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        return json_list[0]['game_start_time'] 
    
    def GetScorecardInfo(self, match_id): 
        ''' 
            reads dynamo and returns game_details 
        ''' 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'scorecard_details')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))

        if len(json_list) < 1: 
            raise ValueError("NO ITEM FOUND FOR THE GIVEN MATCH ID, CHECK THE ID OR CHECK DATABASE")
        else:  
            return json_list[0]['scorecard_details'] 
    
    def GetMatchSquad(self, match_id:str): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'match_squad')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))

        if len(json_list) < 1: 
            raise ValueError("NO ITEM FOUND FOR THE GIVEN MATCH ID, CHECK THE ID OR CHECK DATABASE")
        else:  
            return json_list[0]['match_squad'] 
    

    def CheckIfUserHasSquad(self, match_id, user_id):  
        response = self.squad_table.query( 
                KeyConditionExpression=Key('match_id#user_id').eq(match_id+'#'+str(user_id)),  
                ProjectionExpression = 'squad_selection')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))

        if len(json_list) < 1: 
            return False
        else:  
            return True 
    

    def GetUserSelectedSquad(self, match_id, user_id): 
        response = self.squad_table.query( 
                KeyConditionExpression=Key('match_id#user_id').eq(match_id+'#'+str(user_id)),  
                ProjectionExpression = 'squad_selection')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))  
        if len(json_list) < 1: 
            return None
        return json_list[0]['squad_selection']
        


    ''' ------------------------------------ SETUPGAME ------------------------------------ '''

    def CreateNewGame(self, game_details:GameDetails): 
        dynamo_item = {'match_id': game_details.match_id, 
                       'game_title': game_details.game_title, 
                       'game_status': game_details.game_status, 
                       'squad_link': game_details.squad_link, 
                       'game_start_time': game_details.game_start_time 
                       } 
        
        try:
            response = self.match_table.put_item(Item = dynamo_item)  
            return True
        except: 
            return False  
    

    def AddScoreCardDetails(self, match_id:str, scorecard_details:Dict): 
        update_expression=  "set scorecard_details=:scorecard_details"   
        try:
            response = self.match_table.update_item( 
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
         

    def UpdateSquadLink(self, match_id, new_squad_link): 
        update_expression=  "set squad_link=:squad_link"   
        try:
            response = self.match_table.update_item( 
                Key={'match_id': match_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':squad_link': json.loads(json.dumps(new_squad_link), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )   
            return True 
        except: 
            return False 

    def UpdateStartTime(self, match_id, new_start_time): 
        update_expression=  "set game_start_time=:game_start_time"   
        try:
            response = self.match_table.update_item( 
                Key={'match_id': match_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':game_start_time': json.loads(json.dumps(new_start_time), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )   
            return True 
        except: 
            return False  
    
    def DeleteGame(self, match_id):  
        try:
            response = self.match_table.delete_item(
            Key={'match_id': match_id} 
            ) 
            return True 
        except: 
            return False 
    
    def AddMatchSquad(self, match_id, squad_object): 
        update_expression=  "set match_squad=:match_squad"   
        try:
            response = self.match_table.update_item( 
                Key={'match_id': match_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':match_squad': json.loads(json.dumps(squad_object), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )   
            return True 
        except: 
            return False 


    ''' ------------------------------------ SQUADSELECTION ------------------------------------ '''  
    def AddSelectedSquad(self, match_id, user_id, selected_squad): 
        composite_key = match_id+'#'+str(user_id)
        dynamo_item = {'match_id#user_id': composite_key, # primary composite key
                       'match_id':match_id, 
                       'user_id': user_id, 
                       'squad_selection': json.loads(json.dumps(selected_squad), parse_float=Decimal)
                       } 
        
        try:
            response = self.squad_table.put_item(Item = dynamo_item)  
            return True
        except: 
            return False     
    