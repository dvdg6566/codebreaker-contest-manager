# Manages submission tables
import os
import json
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
SFclient = boto3.client('stepfunctions')

judgeName = os.environ.get('JUDGE_NAME')
accountId = os.environ.get('AWS_ACCOUNT_ID')
region = os.environ.get('AWS_REGION')

counters_table = dynamodb.Table(f'{judgeName}-global-counters')
submissions_table = dynamodb.Table(f'{judgeName}-submissions')
users_table = dynamodb.Table(f'{judgeName}-users')
SUBMISSIONS_BUCKET_NAME = f'{judgeName}-submissions'
stepFunctionARN = f"arn:aws:states:{region}:{accountId}:stateMachine:{judgeName}-grading"
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
def gradeSubmission(problemName,submissionId,username,submissionTime=None,language='cpp',problemType='Batch'):
	
	# If no submission time already recorded, this is a new submission
	if submissionTime == None:
		submissionTime = (datetime.utcnow()+timedelta(hours=8)).strftime("%Y-%m-%d %X")
	
	# Grader required if problem is not batch
	grader = (problemType != 'Batch')

	SF_input = {
		"problemName": problemName,
		"submissionId":int(submissionId),
		"username":username,
		"submissionTime":submissionTime,
		"language":language, 
		"grader": grader,
		"problemType": problemType
	}

	print(json.dumps(SF_input))

	res = SFclient.start_execution(stateMachineArn = stepFunctionARN, input = json.dumps(SF_input))

# SUBMISSION DELAY
def registerSubmission(username, problemName, submissionTime, firstSubmission):
	# Updates users database when user submits to problemName at submissionTime
	# firstSubmission is a counter to track whether this is the users's first submission to the problem
	submissionTime = submissionTime.strftime("%Y-%m-%d %X")
	if firstSubmission: 
		users_table.update_item(
			Key = {'username': username},
			UpdateExpression = 'SET problemSubmissions. #a = :a, latestSubmissions. #a = :b',
			ExpressionAttributeNames = {'#a': problemName},
			ExpressionAttributeValues = {':a': 1, ':b': submissionTime}
		)
	else:
		users_table.update_item(
			Key = {'username': username},
			UpdateExpression = 'ADD problemSubmissions. #a :a SET latestSubmissions. #a = :b',
			ExpressionAttributeNames = {'#a': problemName},
			ExpressionAttributeValues = {':a': 1, ':b': submissionTime}
		)

def checkSubmission(username, problemName, submissionTime, problemInfo):
	# Returns true if submission complies with both submission delay and limit
	subDelay = problemInfo['subDelay']
	subLimit = problemInfo['subLimit']
	resp = users_table.get_item(
		Key= {"username": username },
		ProjectionExpression = 'problemSubmissions. #a, latestSubmissions. #a',
		ExpressionAttributeNames = {'#a': problemName}
	)['Item']

	# No submissions so far 
	if resp == {}: return {'status': 200, 'firstSubmission': True}

	# No time
	latestSubmissionTime = datetime.strptime(resp['latestSubmissions'][problemName], "%Y-%m-%d %X")
	latestSubmissionTime += timedelta(seconds=int(subDelay))
	if latestSubmissionTime > submissionTime:
		return {'status': 300, 
			'error': f'Please wait {subDelay} seconds before submitting!',
			'firstSubmission': False
		}

	problemSubmissions = resp['problemSubmissions'][problemName]
	if problemSubmissions >= subLimit:
		return {'status': 300, 
			'error': f'You have used all {subLimit} submissions to this problem!',
			'firstSubmission': False
		}

	return {'status': 200, 'firstSubmission': False}

''' END: GRADING '''