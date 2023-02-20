#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 18:01:00 2023

@author: Reaz
""" 
from dynamodb_json import json_util as json
import boto3 
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')   
dynamo_client = boto3.client('dynamodb') 
table_name = 'all_match_info'
table = dynamodb.Table(table_name)


def create_table_match_info(table_name):
    table_name = 'all_match_info'
    table = dynamodb.Table(table_name)
    try:
        table.delete()  
        print(f"Deleting {table.name}...")
        table.wait_until_not_exists()
    except: 
        print (f"{table_name} doesn't exist")
    params = { 
        'TableName' : table_name, 
        'KeySchema' : [ 
            { 'AttributeName': 'match_id', 'KeyType': 'HASH'}
            ],  
        'AttributeDefinitions': [
            { 'AttributeName': 'match_id', 'AttributeType': 'S' }
            ], 
        'ProvisionedThroughput': { 'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1 }
    }
        
    
    
    table = dynamodb.create_table(**params)
    print(f"Creating {table_name} ...")
    table.wait_until_exists()
    print(table.item_count) 


def create_table_selected_squads(table_name):
    table_name = 'selected_squads'
    table = dynamodb.Table(table_name)
    try:
        table.delete()  
        print(f"Deleting {table.name}...")
        table.wait_until_not_exists()
    except: 
        print (f"{table_name} doesn't exist")
    params = { 
        'TableName' : table_name, 
        'KeySchema' : [ 
            { 'AttributeName': 'match_id#user_id', 'KeyType': 'HASH'}
            ],  
        'AttributeDefinitions': [
            { 'AttributeName': 'match_id#user_id', 'AttributeType': 'S' }
            ], 
        'ProvisionedThroughput': { 'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1 }
    }
        
    
    
    table = dynamodb.create_table(**params)
    print(f"Creating {table_name} ...")
    table.wait_until_exists()
    print(table.item_count) 


def insert():
    item = {
            'match_id': '12345',  
            'match_title' : 'sa v ind',
            'game_details': {'point_per_run':1, 'point_per_wicket':22, 'start_time': '[2022,1,21,12,0]'} 
           }
    response = table.put_item(Item = item)
    print (response) 

def get_item():  
    response = table.query(
      KeyConditionExpression=Key('match_id').eq('12345')
    )
    x=json.dumps(response["Items"])
    print(response['Items']) 
    print (x)

def gameSetupMirror(): 
    game_details = {'game_title': 'India vs Aus second test', 
                    'game_status': 'Active', 
                    'squad_link': 'https://www.espncricinfo.com/series/australia-in-india-2022-23-1348637/india-vs-australia-2nd-test-1348653/match-squads', 
                    'game_start_time': '[2022,1,19,15,20]',  
                    'scorecard_link': 'https://www.espncricinfo.com/series/australia-in-india-2022-23-1348637/india-vs-australia-2nd-test-1348653/full-scorecard', 
                    'points_per_run': 1,
                    'points_per_wicket': 20,
                    'game_start_time': '[2022,1,19,15,20]' 
                    }
    
    item = {'match_id': '4321', 
            'game_details': game_details
            } 
    response = table.put_item(Item = item)
    print (response)