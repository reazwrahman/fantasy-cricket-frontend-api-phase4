from typing import Dict
import os,sys 
import boto3  
import simplejson as json
from decimal import Decimal 
from boto3.dynamodb.conditions import Key, Attr 

from .models import GameDetails, User

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

        self.users_table_name = 'users' 
        self.users_table = self.dynamodb.Table(self.users_table_name)


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
    
    def GetActiveGamesByIdTitleImage(self): 
        response = self.match_table.scan(
                    FilterExpression=Attr("game_status").eq('Active')
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        active_games = [] 
        for each in json_list:  
            entry = [each['match_id'], each['game_title'], "", "", ""] 
            if 'image' in each: 
                entry[2] = each['image']  
            if "scorecard_link" in each["scorecard_details"]: 
                entry[3] = each["scorecard_details"]["scorecard_link"] 
            if "squad_link" in each: 
                entry[4] = each["squad_link"]
            active_games.append(entry)
        
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

    def GetTeamNames(self, match_id): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'team1')         
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        team1 = json_list[0]['team1']  

        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'team2')   
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True)) 
        team2 = json_list[0]['team2']   

        return [team1, team2] 
    
    def GetMatchResult(self, match_id:str): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'match_result')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))

        if len(json_list) < 1: 
            raise ValueError("NO ITEM FOUND FOR THE GIVEN MATCH ID, CHECK THE ID OR CHECK DATABASE")
        else:  
            return json_list[0]['match_result'] 
    

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
    

    def GetUserSelectedSquad(self, match_id, user_id): 
        response = self.squad_table.query( 
                KeyConditionExpression=Key('match_id#user_id').eq(match_id+'#'+str(user_id)),  
                ProjectionExpression = 'squad_selection')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))  
        if len(json_list) < 1: 
            return None
        return json_list[0]['squad_selection'] 
    

    def GetFantasyRanking(self, match_id): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'fantasy_ranks')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))  
        if 'fantasy_ranks' not in json_list[0]: 
            return None 
        return json_list[0]['fantasy_ranks']  
    
    def GetLastPointsUpdateTime(self, match_id): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'last_updated')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))  
        if 'last_updated' not in json_list[0]: 
            return None  
        
        return json_list[0]['last_updated']
         

    def GetActiveContestantsByUserNames(self, match_id): 
        active_contestants = []  
        response = self.squad_table.scan(
                    FilterExpression=Attr("match_id").eq(match_id)
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True)) 
        for i in range(len(json_list)): 
            squad_selection = json_list[i]['squad_selection']
            user_name = json_list[i]['user_name']  
            active_contestants.append(user_name) 
        
        return active_contestants

    def GetMatchSummaryPoints(self, match_id): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = 'summary_points')   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))

        if len(json_list) < 1: 
            return None
        else:  
            return json_list[0]['summary_points'] 
    
    def GetMatchBreakdownPoints(self, match_id, which_department:str): 
        response = self.match_table.query( 
                KeyConditionExpression=Key('match_id').eq(match_id),  
                ProjectionExpression = which_department)   
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))

        if len(json_list) < 1: 
            return None
        else:  
            return json_list[0][which_department]   
    

    def GetUserMatchPrediction(self, match_id, user_id):
        composite_key = match_id+'#'+str(user_id)
        response = self.squad_table.scan(
                    FilterExpression=Attr("match_id#user_id").eq(composite_key)
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        if len(json_list) < 1: 
            return None
        else:  
            return json_list[0]['squad_selection']['result_prediction'] 

    ''' ------------------------------------ SETUPGAME ------------------------------------ '''

    def CreateNewGame(self, game_details:GameDetails): 
        dynamo_item = {'match_id': game_details.match_id, 
                       'game_title': game_details.game_title, 
                       'game_status': game_details.game_status, 
                       'squad_link': game_details.squad_link, 
                       'game_start_time': game_details.game_start_time, 
                       'team1': game_details.team1, 
                       'team2': game_details.team2, 
                       'match_result': game_details.match_result
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
    
    def DeleteSquads(self, match_id): 
        response = self.squad_table.scan(
                    FilterExpression=Attr("match_id").eq(match_id)
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        
        deletion_successful = True

        for i in range(len(json_list)): 
            partition_key = json_list[i]['match_id#user_id']  
            try:
                response = self.squad_table.delete_item(Key={'match_id#user_id': partition_key})  
            except: 
                deletion_successful = False 
        
        return deletion_successful

        
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
        user_object = self.GetUserById(user_id)
        dynamo_item = {'match_id#user_id': composite_key, # primary composite key
                       'match_id':match_id, 
                       'user_id': user_id,  
                       'user_name': user_object.username,
                       'squad_selection': json.loads(json.dumps(selected_squad), parse_float=Decimal)
                       } 
        
        try:
            response = self.squad_table.put_item(Item = dynamo_item)  
            return True
        except: 
            return False     
    
    ''' ------------------------------------ USERS ------------------------------------ '''   
    def AddUsers(self, user_object:User):  
        dynamo_item = {'user_id': user_object.id, 
                       'user_name': user_object.username,  
                       'email': user_object.email, 
                       'password_hash': user_object.password_hash,   
                       'role': user_object.role,
                       'confirmed': user_object.confirmed
                     } 
        
        response = self.users_table.put_item(Item = dynamo_item) 
        return response['ResponseMetadata']['HTTPStatusCode'] == 200 

    def UpdateUserConfirmation(self, user_id):  
        update_expression=  "set confirmed=:confirmed"  
        response = self.users_table.update_item( 
                Key={'user_id': user_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':confirmed': json.loads(json.dumps(True), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )     
        return response['ResponseMetadata']['HTTPStatusCode'] == 200 
    
    def UpdateUserPassword(self, user_id, password_hash): 
        update_expression=  "set password_hash=:password_hash"  
        response = self.users_table.update_item( 
                Key={'user_id': user_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':password_hash': json.loads(json.dumps(password_hash), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )     
        return response['ResponseMetadata']['HTTPStatusCode'] == 200  
    
    def UpdateUserEmail(self, user_id, email): 
        update_expression=  "set email=:email"  
        response = self.users_table.update_item( 
                Key={'user_id': user_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':email': json.loads(json.dumps(email), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )     
        return response['ResponseMetadata']['HTTPStatusCode'] == 200  
    
    def UpdateUsername(self, user_id, user_name): 
        update_expression=  "set user_name=:user_name"  
        response = self.users_table.update_item( 
                Key={'user_id': user_id}, 
                UpdateExpression= update_expression, 
                ExpressionAttributeValues={
                    ':user_name': json.loads(json.dumps(user_name), parse_float=Decimal)
                },
                ReturnValues="UPDATED_NEW"
            )     
        return response['ResponseMetadata']['HTTPStatusCode'] == 200 
           

    def GetUserConfirmationStatus(self, user_id): 
        response = self.users_table.query( 
                KeyConditionExpression=Key('user_id').eq(user_id),  
                ProjectionExpression = 'confirmed')  
        
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True)) 
        return json_list[0]['confirmed']  
    
    def CheckIfEmailIsUnique(self, email_address): 
        response = self.users_table.scan(
                    FilterExpression=Attr('email').eq(email_address)
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        return len(json_list) == 0
           

    def CheckIfUserNameIsUnique(self, user_name): 
        response = self.users_table.scan(
                    FilterExpression=Attr('user_name').eq(user_name)
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        return len(json_list) == 0  
    
    def GetUserByEmail(self, email_address): 
        response = self.users_table.scan(
                    FilterExpression=Attr('email').eq(email_address.lower())
                    ) 
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True)) 
        if len(json_list) == 0 or len(json_list)>1: 
            return None 
        else:   
            user_object = User(**json_list[0])
            return user_object 
    
    def GetUserById(self, user_id): 
        response = self.users_table.query( 
                KeyConditionExpression=Key('user_id').eq(user_id))
         
        json_list = json.loads(json.dumps(response["Items"], use_decimal=True))
        if len(json_list) == 0 or len(json_list)>1: 
            return None 
        else:   
            user_object = User(**json_list[0])
            return user_object  
    
           
    
           
       