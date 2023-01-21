# Manages DynamoDB Users table

import boto3
from flask import session
from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('codebreakercontest-users')

def getAllUsers():
    return awshelper.scan(users_table)

def getAllUsernames():
    return awshelper.scan(users_table,
        ProjectionExpression = 'username'
    )

# Get user's information based on username
# TODO: Gets the contest info too and returns in as part of object
def getUserInfo(username):
    response = users_table.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    items = response['Items']
    if len(items) != 0: return items[0]
    return None

# Gets information about the currently logged in user based on 
def getCurrentUserInfo():
    if 'username' in dict(session).keys():
        username =  dict(session)['username']
        user_info =  getUserInfo(username)
        return user_info
    else:
        return None

def createUser(username, email, role='member', fullname=''):
    newUserInfo = {
        'email' : email,
        'role' : role,
        'username' : username,
        'fullname': fullname,
        'problemScores' : {},
        'contest': ''
    }
    users_table.put_item(Item = newUserInfo)
    return getUserInfo(email)

# Updates user's info
def updateUserInfo(email, username, fullname, school, theme, hue, nation):
    users_table.update_item(
        Key = {'email' : email},
        UpdateExpression = f'set username =:u, fullname=:f, school =:s, theme =:t, hue=:h, nation=:n',
        ExpressionAttributeValues={':u' : username, ':f' : fullname, ':s' : school, ':t' : theme, ':h':hue, ':n': nation}
    )

def judgeAccess(userInfo):
    if userInfo['role'] == 'admin':
        return True
    # Checks if contest window is ongoing for user and returns true if so
    return False