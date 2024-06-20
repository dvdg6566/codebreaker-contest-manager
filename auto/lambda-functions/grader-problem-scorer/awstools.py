import os
import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

judgeName = os.environ['judgeName']

dynamodb = boto3.resource('dynamodb','ap-southeast-1')
problems_table = dynamodb.Table(f'{judgeName}-problems')
submissions_table = dynamodb.Table(f'{judgeName}-submissions')
users_table = dynamodb.Table(f'{judgeName}-users')
lambda_client = boto3.client('lambda')

def getProblemScores(username):
    response = users_table.query(
        ProjectionExpression = 'problemScores',
        KeyConditionExpression=Key('username').eq(username),
    )
    if len(response['Items']) != 1: return None
    return response['Items'][0]

def getProblemInfo(problemName):
    response = problems_table.query(
        KeyConditionExpression = Key('problemName').eq(problemName)
    )
    if len(response['Items']) != 1: return None
    return response['Items'][0]

def getSubmission(subId):
    response = submissions_table.query(
        KeyConditionExpression = Key('subId').eq(subId)
    )
    if len(response['Items']) != 1: return None
    return response['Items'][0]

def updateSubmission(subId, maxTime, maxMemory, subtaskScores, totalScore):
    gradingCompleteTime = datetime.utcnow().strftime("%Y-%m-%d %X")
    submissions_table.update_item(
        Key={'subId':subId},
        UpdateExpression = f'set maxTime = :a, maxMemory=:b,subtaskScores=:c,totalScore=:d,gradingCompleteTime=:e',
        ExpressionAttributeValues={':a':maxTime,':b':maxMemory,':c':subtaskScores,':d':totalScore,':e':gradingCompleteTime}
    )

def updateCE(subId, compileErrorMessage):
    gradingCompleteTime = datetime.utcnow().strftime("%Y-%m-%d %X")
    submissions_table.update_item(
        Key={'subId':subId},
        UpdateExpression = f'set compileErrorMessage = :a, gradingCompleteTime= :b',
        ExpressionAttributeValues={':a':compileErrorMessage, ':b': gradingCompleteTime}
    )

def getStitchSubmissions(username, problemName):
    # Gets list of all submissions made by user to problem
    submissions = submissions_table.query(
        IndexName = 'usernameIndex',
        KeyConditionExpression = Key('username').eq(username),
        ProjectionExpression = 'subtaskScores, score',
        FilterExpression = Attr('problemName').eq(problemName),
        ScanIndexForward = False
    )['Items']

    return submissions

def updateUserScore(username, problemName, stitchedScore, latestScoreChange):
    users_table.update_item(
        Key = {'username' : username},
        UpdateExpression = f'set problemScores. #a =:a, latestScoreChange=:b',
        ExpressionAttributeValues={':a': stitchedScore, ':b':latestScoreChange},
        ExpressionAttributeNames={'#a':problemName}
    )