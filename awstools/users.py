# Manages DynamoDB Users table
import os
import boto3
from flask import session
from datetime import datetime
from awstools import awshelper, contests
from boto3.dynamodb.conditions import Key

judgeName = os.environ.get('JUDGE_NAME')
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(f'{judgeName}-users')

def getAllUsers():
    return awshelper.scan(users_table)

def getAllUsernames():
    return awshelper.scan(users_table,
        ProjectionExpression = 'username'
    )

def getAllUserContests():
    return awshelper.scan(users_table,
        ProjectionExpression = 'username, contest'
    )

# Get user's information based on username
# TODO: Gets the contest info too and returns in as part of object
def getUserInfo(username):
    response = users_table.get_item(
        Key={'username': username}
    )
    if 'Item' not in response.keys(): return None
    return response['Item']

# Gets information about the currently logged in user based on Flask cookies
def getCurrentUserInfo():
    if 'username' in dict(session).keys():
        username =  dict(session)['username'] 
        return getUserInfo(username)
    else:
        return None

def createUser(username, role, fullname='', email='', label=''):
    if fullname == '': fullname = username
    newUserInfo = {
        'username' : username,
        'role' : role,
        'fullname': fullname,
        'contest': '',
        'problemScores' : {},
        'problemSubmissions': {},
        'latestSubmissions': {}, 
        'latestScoreChange': '',
        'label': label,
        'email': email
    }
    users_table.put_item(Item = newUserInfo)

# Sets all the users to have contestId
# Returns list of fail operations: if any of the users have already participated in contest
def setContest(usernames, contestId):
    contestTimes = contests.getAllContestTimes()
    curtime = datetime.utcnow()

    usersInfo = awshelper.batchGetItems(f'{judgeName}-users', usernames, 'username')
    failUsers = [] # Users that can't be updated
    for user in usersInfo:
        fail = 0
        if user['contest'] != '':
            userContestId = user['contest']
            if userContestId in contestTimes and contestTimes[userContestId]['startTime'] < curtime: 
                fail = 1
        if fail: 
            failUsers.append(user['username'])
        else:
            users_table.update_item(
                Key = {'username': user['username']},
                UpdateExpression = f'set #a=:a',
                ExpressionAttributeNames = {'#a': 'contest'},
                ExpressionAttributeValues = {':a': contestId}
            )
    return failUsers

def judgeAccess(userInfo):
    if userInfo['role'] == 'admin':
        return True
    # Checks if contest window is ongoing for user and returns true if so
    return False