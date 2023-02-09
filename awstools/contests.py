import os
import boto3
from awstools import awshelper
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

judgeName = os.environ.get('JUDGE_NAME')
contests_table = dynamodb.Table(f'{judgeName}-contests')

def getAllContestIds():
	contestIds = awshelper.scan(contests_table, ProjectionExpression='contestId')
	return [i['contestId'] for i in contestIds]

def getAllContestInfo():
	return awshelper.scan(contests_table)

# gets all start times when adding users into contests
def getAllContestTimes():
    contestsInfo = getAllContestInfo()
    contestTimes = {}
    for contest in contestsInfo:
        contestTimes[contest['contestId']] = {
        	'startTime': datetime.strptime(contest['startTime'], "%Y-%m-%d %X"),
        	'endTime': datetime.strptime(contest['endTime'], "%Y-%m-%d %X")
       	}
    return contestTimes

def getContestInfo(contestId):
	response = contests_table.query(
		KeyConditionExpression = Key('contestId').eq(contestId)
	)
	contest_info=response['Items']
	if len(contest_info) == 0:
		return None
	return contest_info[0]

def updateContestInfo(contestId, info):
	contests_table.update_item(
		Key = {'contestId' : contestId},
		UpdateExpression = f'set description=:b, contestName=:c, problems=:d, #u=:e, startTime=:f, endTime=:g, subLimit=:h, subDelay=:i',
		ExpressionAttributeValues={':b':info['description'],':c':info['contestName'],':d':info['problems'],':e':info['users'], ':f':info['startTime'],':g':info['endTime'],':h':info['subLimit'],':i':info['subDelay']},
		ExpressionAttributeNames={'#u':'users'}
	)

def updateContestTable(contestId, info):
	contests_table.update_item(
		Key = {'contestId' : contestId},
		UpdateExpression = f'set description=:b, contestName=:c, startTime=:d, endTime=:e',
		ExpressionAttributeValues={':b':info['description'],':c':info['contestName'], ':d':info['startTime'],':e':info['endTime']}
	)

def createContest(contestId):
	info = {}
	info['contestId'] = contestId
	info['description'] = f'Default description for id: {contestId}'
	info['contestName'] = 'New Contest'
	info['problems'] = []
	info['users'] = {}
	info['startTime'] = (datetime(9999, 12, 1, 5, 0, 0)).strftime("%Y-%m-%d %X")
	info['endTime'] =  (datetime(9999, 12, 1, 11, 0, 0)).strftime("%Y-%m-%d %X")
	info['subLimit'] = 50
	info['subDelay'] = 60
	updateContestInfo(contestId, info)