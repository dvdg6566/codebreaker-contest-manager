# Invokes lambda functions to ping websockets
# If performance degrades, can consider using EC2 side to trigger Step Function

import os
import json
import boto3
lambda_client = boto3.client('lambda')

judgeName = os.environ.get('JUDGE_NAME')
accountId = os.environ.get('AWS_ACCOUNT_ID')
region = os.environ.get('AWS_REGION')

WEBSOCKET_INVOKE_LAMBDA_NAME = f'arn:aws:lambda:{region}:{accountId}:function:{judgeName}-websocket-invoke'

def announce():
	# Ping all users
	lambda_input = {'notificationType': 'announce'}
	res = lambda_client.invoke(FunctionName = WEBSOCKET_INVOKE_LAMBDA_NAME, InvocationType='Event', Payload = json.dumps(lambda_input))
	print(res)

def postClarification():
	# Ping all admins
	lambda_input = {'notificationType': 'postclarification'}
	res = lambda_client.invoke(FunctionName = WEBSOCKET_INVOKE_LAMBDA_NAME, InvocationType='Event', Payload = json.dumps(lambda_input))

def answerClarification(username):
	# Ping any connection for specified username
	lambda_input = {'notificationType': 'answerclarification', 'username': username}
	res = lambda_client.invoke(FunctionName = WEBSOCKET_INVOKE_LAMBDA_NAME, InvocationType='Event', Payload = json.dumps(lambda_input))