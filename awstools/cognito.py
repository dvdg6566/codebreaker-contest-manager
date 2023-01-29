# Manages authentication and logins
import os
import boto3
from awstools import users
from botocore.exceptions import ClientError

clientId = os.environ.get('COGNITO_CLIENT_ID')
client = boto3.client('cognito-idp')

def authenticate(username, password):
	try:
		response = client.initiate_auth(
			AuthFlow = 'USER_PASSWORD_AUTH',
			AuthParameters = {
				"USERNAME" : username,
		      	"PASSWORD" : password
			},
			ClientId = clientId
		)
		
		return {'status': 200, 'username': username}
		
	except ClientError as e:
		if e.response['Error']['Code'] == 'NotAuthorizedException':
			return {'status': 403}
		else:
			return {'status':400}

def createUser (username, email, role):
	response = client.admin_create_user(
		UserPoolId = 'ap-southeast-1_xiTNBPfQ3',
		Username = username,
		DesiredDeliveryMediums = ['EMAIL'],
		UserAttributes=[
			{
				'Name': 'email',
				'Value': email
			}
		]
	)

	# response = client.admin_confirm_sign_up(
	# 	UserPoolId = 'ap-southeast-1_xiTNBPfQ3',
	# 	Username=username,	
	# )

	# Create dynamo db element
	users.createUser(username, email, role)