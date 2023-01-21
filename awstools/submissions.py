# Manages submission tables

import json
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
SFclient = boto3.client('stepfunctions')

judgeName = 'codebreakercontest'
counters_table = dynamodb.Table(f'{judgeName}-global-counters')
submissions_table = dynamodb.Table(f'{judgeName}-submissions')
SUBMISSIONS_BUCKET_NAME = f'{judgeName}-submissions'
subPerPage = 25

# Submission View page: Gets all details to do with submission 
def getSubmission(subId):
	response= submissions_table.get_item( Key={ "subId": subId } )
	
	if 'Item' not in response.keys(): return None
	subDetails = response['Item']
	if subDetails['language'] == 'py':
		pyfile = s3.get_object(Bucket=SUBMISSIONS_BUCKET_NAME, Key=f'source/{subId}.py')
		code = pyfile['Body'].read().decode("utf-8")
		subDetails['code'] = code
	else:
		try:
			cppfile = s3.get_object(Bucket=SUBMISSIONS_BUCKET_NAME, Key=f'source/{subId}.cpp')
			code = cppfile['Body'].read().decode("utf-8")
			subDetails['code'] = code
		except:
			cppfile = s3.get_object(Bucket=SUBMISSIONS_BUCKET_NAME, Key=f'source/{subId}A.cpp')
			codeA = cppfile['Body'].read().decode("utf-8")
			subDetails['codeA'] = codeA
			cppfile = s3.get_object(Bucket=SUBMISSIONS_BUCKET_NAME, Key=f'source/{subId}B.cpp')
			codeB = cppfile['Body'].read().decode("utf-8")
			subDetails['codeB'] = codeB

	return subDetails

''' BEGIN: SUBMISSIONS PAGE '''
# Get number of submissions gets the glboal number of submissions to control page number in submissions page
def getNumberOfSubmissions():
	resp = counters_table.query(
		KeyConditionExpression = Key('counterId').eq('submissionId')
	)
	item = resp['Items'][0]
	subId = int(item['value'])
	return subId

# Batch get functions is a helper function for unfiltered global submission list
def batchGetSubmissions(start, end):
	submissions = []
	for i in range(start, end+1):
		submissions.append({'subId' : i})
	response = dynamodb.batch_get_item(
		RequestItems={
			f'{judgeName}-submissions': {
				'Keys': submissions,            
				'ConsistentRead': True,
				'ProjectionExpression': 'subId, problemName, submissionTime, username, #a, totalScore, maxTime, maxMemory',
				'ExpressionAttributeNames': {'#a': 'language'}
			}
		},
		ReturnConsumedCapacity='TOTAL'
	)
	return response

def getSubmissionsList(pageNo, problem, username): 
	# All submissions: Calculate range of indeces and use batch get
	if username == None and problem == None:
		latest = int(getNumberOfSubmissions())
		end = latest - (pageNo-1)* subPerPage
		start = max(1, end-subPerPage+1)

		if end < 0:
			return []

		response = batchGetSubmissions(start,end)
		submissions = response['Responses'][f'{judgeName}-submissions']
		return submissions

	# When username of problem is being filtered, use global secondary index to filter
	elif username != None and problem == None:
		response = submissions_table.query(
			IndexName = 'usernameIndex',
			KeyConditionExpression=Key('username').eq(username),
			Limit = (pageNo+1)*subPerPage + 2,
			ProjectionExpression = 'subId, maxMemory, maxTime, problemName, submissionTime, totalScore, username, #a, compileErrorMessage',
			ExpressionAttributeNames = {'#a': 'language'},
			ScanIndexForward = False
		)
		return response['Items']
	elif username == None and problem != None:
		response = submissions_table.query(
			IndexName = 'problemIndex',
			KeyConditionExpression=Key('problemName').eq(problem),
			ProjectionExpression = 'subId, maxMemory, maxTime, problemName, submissionTime, totalScore, username, #a, compileErrorMessage',
			ExpressionAttributeNames = {'#a': 'language'},
			Limit = (pageNo+1)*subPerPage + 2,
			ScanIndexForward = False
		)
		return response['Items']

	# When nothing filtered: Use problem index to filter and sub-filter by username
	else:
		response = submissions_table.query(
			IndexName = 'problemIndex',
			KeyConditionExpression=Key('problemName').eq(problem),
			ProjectionExpression = 'subId, maxMemory, maxTime, problemName, submissionTime, totalScore, username, #a, compileErrorMessage',
			ExpressionAttributeNames = {'#a': 'language'},
			FilterExpression = Attr('username').eq(username),
			ScanIndexForward = False
		)
		return response['Items']

''' END: SUBMISSION PAGE '''
''' BEGIN: GRADING '''

def getNextSubmissionId():
	resp = counters_table.update_item(
		Key = {'counterId': 'submissionId'},
		UpdateExpression = 'ADD #a :x',
		ExpressionAttributeNames = {'#a' : 'value'},
		ExpressionAttributeValues = {':x' : 1},
		ReturnValues = 'UPDATED_NEW'
	)
	subId = int(resp['Attributes']['value'])
	return subId

# UPLOAD CODE OF SUBMISSION TO S3 
def uploadSubmission(code, s3path):
	s3_resource.Object(SUBMISSIONS_BUCKET_NAME, s3path).put(Body=code)

# Sends submission to be regraded by Step Function
def gradeSubmission(problemName,submissionId,username,submissionTime=None,regradeall=False,language='cpp',problemType='Batch'):
	regrade=True

	# If no submission time already recorded, this is a new submission
	if submissionTime == None:
		regrade=False
		submissionTime = (datetime.utcnow()+timedelta(hours=8)).strftime("%Y-%m-%d %X")
	
	# Grader required if problem is not batch
	grader = (problemType != 'Batch')

	SF_input = {
		"problemName": problemName,
		"submissionId":int(submissionId),
		"username":username,
		"submissionTime":submissionTime,
		"stitch":1, # Stitch should always be 1
		"regrade":regrade,
		"regradeall":regradeall,
		"language":language, 
		"grader": grader,
		"problemType": problemType
	}

	stepFunctionARN = "arn:aws:states:ap-southeast-1:354145626860:stateMachine:Codebreaker-grading-v3"
	res = SFclient.start_execution(stateMachineArn = stepFunctionARN, input = json.dumps(SF_input))

''' END: GRADING '''