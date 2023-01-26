import os
import boto3
from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

judgeName = os.environ.get('JUDGE_NAME')
contests_table = dynamodb.Table(f'{judgeName}-contests')

# Gets timezone from environment variables
TIMEZONE_OFFSET = os.environ.get('TIMEZONE_OFFSET')

def getAllContestIds():
	contestIds = awshelper.scan(contests_table, ProjectionExpression='contestId')
	return contestIds

def getAllContestInfo():
	print(TIMEZONE_OFFSET)
	return awshelper.scan(contests_table,
		ProjectionExpression = 'contestId, contestName, startTime, endTime, #PUBLIC, #DURATION, #USERS',
		ExpressionAttributeNames={ "#PUBLIC": "public", "#DURATION" : "duration", '#USERS':'users' } #not direct cause users is a reserved word
	)

def getAllContestsLimited():
	return awshelper.scan(contests_table,
		ProjectionExpression = 'contestId, contestName, startTime, endTime, #PUBLIC',
		ExpressionAttributeNames={ "#PUBLIC": "public"} #not direct cause users is a reserved word
	)

def getContestInfo(contestId):
	response = contests_table.query(
		KeyConditionExpression = Key('contestId').eq(contestId)
	)
	contest_info=response['Items']
	if len(contest_info) == 0:
		return None
	return contest_info[0]

def updateContestInfo(contest_id, info):
	if info['endTime'] != "Unlimited":
		testtime = datetime.strptime(info['endTime'], "%Y-%m-%d %X")
	testtime = datetime.strptime(info['startTime'], "%Y-%m-%d %X")
	contests_table.update_item(
		Key = {'contestId' : contest_id},
		UpdateExpression = f'set contestName=:b, #wtf=:c, problems=:d, #kms=:e, #die=:f, scores=:g, startTime=:h, endTime=:i, description=:j, publicScoreboard=:k, editorial=:l, editorialVisible=:m, subLimit=:n, subDelay=:o',
		ExpressionAttributeValues={':b':info['contestName'], ':c':info['duration'], ':d':info['problems'], ':e':info['public'], ':f':info['users'], ':g':info['scores'], ':h':info['startTime'], ':i':info['endTime'], ':j':info['description'], ':k':info['publicScoreboard'], ':l':info['editorial'], ':m':info['editorialVisible'], ':n':info['subLimit'], ':o':info['subDelay']},
		ExpressionAttributeNames={'#wtf':'duration', '#kms':'public', '#die':'users'}
	)
	addParticipation(contest_id, "ALLUSERS")
	recalcContestInfo()
	return True

def createContestWithId(contest_id):
	info = {}
	info['description'] = ''
	info['contestId'] = contest_id
	info['contestName'] = 'New Contest'
	info['duration'] = 0
	info['problems'] = []
	info['public'] = False
	info['publicScoreboard'] = False
	info['users'] = {}
	info['scores'] = {}
	info['startTime'] = (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %X")
	info['endTime'] =  "Unlimited"
	info['editorial'] = ""
	info['editorialVisible'] = False
	info['subLimit'] = -1
	info['subDelay'] = 10
	updateContestInfo(contest_id, info)