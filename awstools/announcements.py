import boto3
from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

judgeName = 'codebreaker'
announce_table = dynamodb.Table(f'{judgeName}-announcements')

# Gets all announcements for homepage
def getAllAnnounces():
	return awshelper.scan(announce_table, 
		ProjectionExpression='announceId, priority, visible, aSummary, aTitle, adminOnly, contestLink'
	)

# Detailed view of announcement
def getAnnounceWithId(announceId):
	response=announce_table.query(
		KeyConditionExpression = Key('announceId').eq(announceId)
	)
	info=response['Items']
	if len(info) == 0: return "This announcement doesn't exist"
	if len(info) != 1: return "An error has occurred"

	info = info[0]
	return info

def updateAnnounce(announceId, info):
	announce_table.update_item(
		Key = {'announceId': announceId},
		UpdateExpression = f'set priority=:a, visible=:b, aTitle=:c, aSummary=:d, aText=:e, adminOnly=:f, contestLink = :g',
		ExpressionAttributeValues={':a':info['priority'], ':b':info['visible'], ':c':info['aTitle'], ':d':info['aSummary'], ':e':info['aText'], ':f':info['adminOnly'], ':g':info['contestLink']}
	)

def createAnnounceWithId(announceId):
	ann = getAllAnnounces()
	info = {}
	info['priority'] = 1
	for an in ann:
		info['priority'] = max(info['priority'], an['priority']+1)
	info['announceId'] = announceId
	info['visible'] = False
	info['adminOnly'] = False
	info['aTitle'] = announceId
	info['aSummary'] = "default summary of announce"
	info['aText'] = "default text of announce"
	info['contestLink'] = ""
	updateAnnounce(announceId, info)
