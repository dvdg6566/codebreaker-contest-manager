import os
import json
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

lambda_client = boto3.client('lambda')
SFclient = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')
s3_resource = boto3.resource('s3')

judgeName = os.environ.get('JUDGE_NAME')
accountId = os.environ.get('AWS_ACCOUNT_ID')
region = os.environ.get('AWS_REGION')

counters_table = dynamodb.Table(f'{judgeName}-global-counters')
stepFunctionARN = f"arn:aws:states:{region}:{accountId}:stateMachine:{judgeName}-grading"
SUBMISSIONS_BUCKET_NAME = f'{judgeName}-submissions'

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
def startGrading(problemName,submissionId,username,submissionTime=None,language='cpp',problemType='Batch'):
	
	# If no submission time already recorded, this is a new submission
	if submissionTime == None:
		submissionTime = (datetime.utcnow()).strftime("%Y-%m-%d %X")
	
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

	# SUBDELAY
	latestSubmissionTime = datetime.strptime(resp['latestSubmissions'][problemName], "%Y-%m-%d %X")
	latestSubmissionTime += timedelta(seconds=int(subDelay))
	if latestSubmissionTime > submissionTime:
		return {'status': 300, 
			'error': f'Please wait {subDelay} seconds before submitting!',
			'firstSubmission': False
		}

	# SUBLIMIT
	problemSubmissions = resp['problemSubmissions'][problemName]
	if problemSubmissions >= subLimit:
		return {'status': 300, 
			'error': f'You have used all {subLimit} submissions to this problem!',
			'firstSubmission': False
		}

	return {'status': 200, 'firstSubmission': False}

def gradeSubmission(form, problemInfo, userInfo, language):
	''' DOES VALIDATION ON SUBMISSION AND TRIGGERS STEP FUNCTION '''
	
	problemName = problemInfo['problemName']
	username = userInfo['username']

	''' BLOCK DISABLED OR NON-USERS FROM SUBMITTING '''
	if userInfo == None:
		return {'status': 300, 'error':'You do not have permission to submit!'}
		
	if not problemInfo['validated']:
		return {'status': 300, 'error':'Sorry, this problem is still incomplete.'}

	''' CHECKS LENGTH OF CODE '''
	code, codeA, codeB = '','',''
	if problemInfo['problem_type'] == 'Communication':
		codeA = form['codeA']
		codeB = form['codeB']
	else:
		code = form['code']

	if max(len(code), len(codeA), len(codeB)) > 128000:
		return {'status': 300, 'error': 'Sorry, your code is too long!'}

	# Assign new submission index
	subId = getNextSubmissionId()

	if problemInfo['problem_type'] == 'Communication':
		# Upload code file to S3
		s3pathA = f'source/{subId}A.{language}'
		s3pathB = f'source/{subId}B.{language}'
		uploadSubmission(code = codeA, s3path = s3pathA)
		uploadSubmission(code = codeB, s3path = s3pathB)
	else:
		# Upload code file to S3
		s3path = f'source/{subId}.{language}'
		uploadSubmission(code = code, s3path = s3path)

	# Grade submission
	startGrading(
		problemName = problemName,
		submissionId = subId,
		username = userInfo['username'],
		submissionTime = None,
		language = language,
		problemType = problemInfo['problem_type']
	)

	return {'status':200, 'subId':subId}