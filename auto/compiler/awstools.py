import boto3
import json
import os

judgeName = os.environ['judgeName']
SUBMISSIONS_BUCKET_NAME = f'{judgeName}-submissions'
CHECKERS_BUCKET_NAME = f'{judgeName}-checkers'
GRADERS_BUCKET_NAME = f'{judgeName}-graders'

s3 = boto3.client('s3','ap-southeast-1')
dynamodb = boto3.resource('dynamodb', 'ap-southeast-1')
problems_table = dynamodb.Table(f'{judgeName}-problems')

def getGraderFile(s3path, localpath):
	grader = s3.get_object(Bucket=GRADERS_BUCKET_NAME,Key=s3path)
	grader = grader['Body'].read().decode('utf-8')
	with open(localpath,"w") as f:
		f.write(grader)
		f.close()

def getSubmission(s3path, localpath):
	tcfile = s3.get_object(Bucket=SUBMISSIONS_BUCKET_NAME, Key=s3path)
	body = tcfile['Body'].read().decode("utf-8")
	with open(localpath,"w") as f:
		f.write(body)
		f.close()

def uploadCode(localpath, s3path):
	s3.upload_file(localpath, SUBMISSIONS_BUCKET_NAME, s3path)

# GET COMMUNICATION PROBLEM FILE NAMES
def getCommunicationFileNames(problemName):
	res = problems_table.get_item(
		Key = {'problemName' : problemName},
		ProjectionExpression = 'nameA, nameB'
	)['Item']
	return res

def getChecker(s3path, localpath):
	tcfile = s3.get_object(Bucket=CHECKERS_BUCKET_NAME, Key=s3path)
	body = tcfile['Body'].read().decode("utf-8")
	with open(localpath,"w") as f:
		f.write(body)
		f.close()

def uploadCompiledChecker(localpath, s3path):
	s3.upload_file(localpath, CHECKERS_BUCKET_NAME, s3path)