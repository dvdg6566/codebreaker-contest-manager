import os
import boto3
import json
from time import sleep
from botocore.exceptions import ClientError

iam_client = boto3.client('iam')
sts_client = boto3.client('sts')
accountId = os.environ.get('AWS_ACCOUNT_ID')
judgeName = os.environ.get('JUDGE_NAME')

def createRole(problemName):
	roleName = f'{judgeName}-testdata-{problemName}-role'

	policyDocument = {
		'Version':'2012-10-17', 
		'Statement': [{ 
			'Sid': 'AllowS3PutItemInTestcaseFolder', 
			'Effect': 'Allow', 
			'Action': ['s3:PutObject'], 
			'Resource': [f'arn:aws:s3:::{judgeName}-testdata/{problemName}/*'] 
	   }] 
	}

	assumeRolePolicyDocument = {
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Principal": {
					"AWS": [
						f"arn:aws:iam::{accountId}:role/{judgeName}-ec2main",
						f"arn:aws:iam::{accountId}:user/orange"
					] # Allow EC2 main for EC2, and orange for local testing
				},
				"Action": "sts:AssumeRole",
				"Condition": {}
			}
		]
	}

	try:
		# Create role with trust relationship for EC2 to use
		resp = iam_client.create_role(
			RoleName = roleName,
			AssumeRolePolicyDocument = json.dumps(assumeRolePolicyDocument),
			Description = f"Role that grants admins permission to upload testdata to {problemName}",
			MaxSessionDuration = 3600
		)

		sleep(5)

		arn = resp['Role']['Arn']

		# IAM policy limits permissions to PutObject access to specific folder of testdata bucket
		iam_client.put_role_policy(
			RoleName=roleName,
			PolicyName='S3AccessPolicy',
			PolicyDocument=json.dumps(policyDocument)
		)

		# Permissions boundary limited to S3 with managed policy
		iam_client.put_role_permissions_boundary(
			RoleName=roleName,
			PermissionsBoundary="arn:aws:iam::aws:policy/AmazonS3FullAccess"
		)

		sleep(5)
		return arn

	except ClientError as e:

		if e.response['Error']['Code'] == 'EntityAlreadyExists':
			resp = iam_client.get_role(RoleName=roleName)
			arn = resp['Role']['Arn']
			return arn
		else:
			return ''

def getTokens(problemName):
	arn = createRole(problemName)
	
	resp = sts_client.assume_role(RoleArn=arn,RoleSessionName="Testing",DurationSeconds=1800)
	accessKey = resp['Credentials']['AccessKeyId']
	secretAccessKey = resp['Credentials']['SecretAccessKey']
	sessionToken = resp['Credentials']['SessionToken']

	return {
		'accessKeyId': accessKey,
		'secretAccessKey': secretAccessKey,
		'sessionToken': sessionToken
	}