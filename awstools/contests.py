import os
import boto3
from awstools import awshelper
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

judgeName = os.environ.get('JUDGE_NAME')
contests_table = dynamodb.Table(f'{judgeName}-contests')
users_table = dynamodb.Table(f'{judgeName}-users')

# Helper function to convert contest timing to UTC timestring and define status of contest
def getContestStatus(contest):
	contest['endTime'] = datetime.strptime(contest['endTime'], "%Y-%m-%d %X")
	contest['startTime'] = datetime.strptime(contest['startTime'], "%Y-%m-%d %X")
	curTime = datetime.utcnow()

	if curTime > contest['endTime']:
		contest['status'] = 'ENDED'
	elif curTime <= contest['endTime'] and curTime >= contest['startTime']:
		contest['status'] = 'ONGOING'
	else:
		contest['status'] = 'NOT_STARTED'

	return contest

def getAllContestIds():
	contestIds = awshelper.scan(
		table=contests_table, 
		ProjectionExpression='contestId'
	)
	return [i['contestId'] for i in contestIds]

def getAllContestInfo():
	contestsInfo = awshelper.scan(contests_table)
	for contest in contestsInfo:
		contest = getContestStatus(contest)
	return contestsInfo

# gets all start times (in UTC) when adding users into contests
def getAllContestTimes():
	contestsInfo = awshelper.scan(
		table=contests_table, 
		ProjectionExpression='contestId, startTime, endTime'
	)
	contestTimes = {}
	for contest in contestsInfo:
		contestTimes[contest['contestId']] = {
			'startTime': datetime.strptime(contest['startTime'], "%Y-%m-%d %X"),
			'endTime': datetime.strptime(contest['endTime'], "%Y-%m-%d %X")
		}
	return contestTimes

def getContestInfo(contestId):
	if contestId == '': return None
	response = contests_table.get_item(
		Key = {'contestId': contestId}
	)
	if 'Item' not in response: return None	
	contest = response['Item']
	
	return getContestStatus(contest)

def updateContestInfo(contestId, info):
	contests_table.update_item(
		Key = {'contestId' : contestId},
		UpdateExpression = f'set contestName=:b, problems=:c, startTime=:d, endTime=:e, subLimit=:f, subDelay=:g',
		ExpressionAttributeValues={':b':info['contestName'],':c':info['problems'],':d':info['startTime'],':e':info['endTime'],':f':info['subLimit'],':g':info['subDelay']},
	)

def updateContestTable(contestId, info):
	contests_table.update_item(
		Key = {'contestId' : contestId},
		UpdateExpression = f'set startTime=:a, endTime=:b',
		ExpressionAttributeValues={':a':info['startTime'],':b':info['endTime']}
	)

# Sets all the users to have contestId
# Returns list of fail operations: if any of the users have already participated in contest
def setContest(usernames, contestId):
	print(usernames, contestId)
	contestTimes = getAllContestTimes()
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

def createContest(contestId):
	info = {}
	info['contestId'] = contestId
	info['contestName'] = 'New Contest'
	info['problems'] = []
	info['startTime'] = (datetime(9999, 12, 1, 5, 0, 0)).strftime("%Y-%m-%d %X")
	info['endTime'] =  (datetime(9999, 12, 1, 11, 0, 0)).strftime("%Y-%m-%d %X")
	info['subLimit'] = 50
	info['subDelay'] = 60
	updateContestInfo(contestId, info)