# Script to initialise codebuild project, waits for project completion and creqates lambda function from the created ECR image

# AWS CloudFormation is a service that is used for infrastructure as code and it is primarily used for creating and managing AWS resources. While it can create and configure AWS CodeBuild projects, it does not have the capability to directly initialize a CodeBuild build.
# To start a build in AWS CodeBuild, you need to use the StartBuild API action, either through the AWS CLI or through the AWS SDKs. This API call can be triggered by an event, such as a commit to a source code repository, or it can be initiated manually.

import os
import boto3
from time import sleep

# Loads environment variables using dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
judgeName = os.environ.get('JUDGE_NAME')
accountId = os.environ.get('AWS_ACCOUNT_ID')
region = os.environ.get('AWS_REGION')

codeBuildClient = boto3.client('codebuild')
lambda_client = boto3.client('lambda')

projectName = f'{judgeName}-codebuildproject'
lambdaFunctionName = f'{judgeName}-compiler'
lambdaRoleArn = f'arn:aws:iam::{accountId}:role/{judgeName}-compiler-role'
imageUri = f'{accountId}.dkr.ecr.{region}.amazonaws.com/{judgeName}-compiler-repository:latest'
print(lambdaRoleArn)

def initBuild():
	# Initialises codebuild project created by SAM
	resp = codeBuildClient.start_build(
		projectName = projectName
	)
	buildId = resp['build']['id']

	return buildId

def waitForCompletion(buildId):
	status = 'IN_PROGRESS'
	while status == 'IN_PROGRESS':
		sleep(20)

		response = codeBuildClient.batch_get_builds(ids=[buildId])
		status = response['builds'][0]['buildStatus']

		print(status)
	return status

def createLambda():
	# Creates lambda from ECR
	response = lambda_client.create_function(
    	FunctionName=lambdaFunctionName,
	    PackageType='Image',
	    Code={'ImageUri': imageUri},
	    Role= lambdaRoleArn,
	    Environment = {
	    	'Variables': {
    			'AWS_ACCOUNT_ID': accountId,
    			'judgeName': judgeName
	    	}
	    },
	    Timeout = 60,
	    MemorySize = 1600
	)
	# print(response)

if __name__ == '__main__':
	buildId = initBuild()

	print(f"Build Id: {buildId}")
	print("Waiting for build completion...")
	sleep(120)

	status = waitForCompletion(buildId)

	if status == 'SUCCEEDED':
		createLambda()

'''
	{
	"submissionId": 27,
	"grader": false, 
	"problemType": "Batch",
	"language": "cpp",
	"problemName": "addition",
	"username": "sgz002",
	"submissionTime": "placeholder"
}
'''