# Gets list of 

import os
import json
import boto3
from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
SFclient = boto3.client('stepfunctions')

judgeName = os.environ.get('JUDGE_NAME')
accountId = os.environ.get('AWS_ACCOUNT_ID')
region = os.environ.get('AWS_REGION')
WEBSOCKET_STEP_FUNCTION_ARN = f'arn:aws:states:{region}:{accountId}:stateMachine:{judgeName}-websocket'

websocket_table = dynamodb.Table(f'{judgeName}-websocket')

def announce():
	# Ping all users
	items = awshelper.scan(websocket_table, ProjectionExpression='connectionId')
	invoke(items,'announce')

def postClarification():
	# Ping all admins
	items = websocket_table.query(
		IndexName = 'accountRoleUsernameIndex',
		KeyConditionExpression = Key('accountRole').eq('admin'),
		ProjectionExpression='connectionId'
	)['Items']
	invoke(items, 'postClarification')

def answerClarification(role, username):
	# Ping any connection for specified username
	items = websocket_table.query(
		IndexName = 'accountRoleUsernameIndex',
		KeyConditionExpression = Key('accountRole').eq(role) & Key('username').eq(username),
		ProjectionExpression='connectionId'
	)['Items']
	
	invoke(items, 'answerClarification')

def invoke(items, notificationType):
	connectionIds = [i['connectionId'] for i in items]
	# Formats items for step function, grouping items in sets of 100 with list comprehension
	BLOCK_SIZE = 100
	buckets = [connectionIds[i: i+BLOCK_SIZE] for i in range(0, len(connectionIds), BLOCK_SIZE)]

	# print(buckets)
	SF_input = json.dumps([{
		'notificationType': notificationType,
		'connectionIds': i
	} for i in buckets])
	
	res = SFclient.start_execution(stateMachineArn = WEBSOCKET_STEP_FUNCTION_ARN, input = SF_input)
