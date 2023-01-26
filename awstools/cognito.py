# Manages authentication and logins
import os
import boto3
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