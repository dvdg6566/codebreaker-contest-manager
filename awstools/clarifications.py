import os
import boto3
from datetime import datetime

from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

judgeName = os.environ.get('JUDGE_NAME')
clarifications_table = dynamodb.Table(f'{judgeName}-clarifications')

def createClarification(username, problemName, question):
	info = {}
	info['askedBy'] = username
	info['problemName'] = problemName
	info['question'] = question
	info['clarificationTime'] = str(datetime.utcnow().strftime("%Y-%m-%d %X"))
	info['answer'] = ""
	info['answeredBy'] = ""
	clarifications_table.put_item(Item=info)
	# Notify admins of new clarification

def answerClarification(askedBy, clarificationTime, answer, answeredBy):
	# askedBy, clarificationTime form composite primary key
	resp = clarifications_table.update_item(
		Key = {'askedBy':askedBy, 'clarificationTime': clarificationTime},
		UpdateExpression = f'set answer=:a,answeredBy=:b',
		ExpressionAttributeValues={':a':answer,':b':answeredBy}
	)
	# Notify user that clarification has been answered

def getClarificationsByUser(username):
	response = clarifications_table.query(
		KeyConditionExpression = Key('askedBy').eq(username)
	)
	return response['Items']

def getAllClarifications():
	return awshelper.scan(clarifications_table)