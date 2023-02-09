# Manages authentication and logins
import os
import boto3
import string
import secrets
from awstools import users
from botocore.exceptions import ClientError

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

userPoolId = os.environ.get('COGNITO_USER_POOL_ID')
clientId = os.environ.get('COGNITO_CLIENT_ID')
client = boto3.client('cognito-idp')

def generateSecurePassword():
	# Generates secure password to set when creating member accounts
	alphabet = string.ascii_letters + string.digits + string.punctuation
	password = ''.join(secrets.choice(alphabet) for i in range(8))  # for a 20-character password
	return password

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
		print(e)
		if e.response['Error']['Code'] == 'NotAuthorizedException':
			return {'status': 403}
		else:
			return {'status':400}

def createUser (username, role, email=''):
	# For admin role: Create user and let cognito send email
	if role == 'admin':
		if email == '':
			return {'status': 400}

		response = client.admin_create_user(
			UserPoolId = userPoolId,
			Username = username,
			DesiredDeliveryMediums = ['EMAIL'],
			UserAttributes=[
				{
					'Name': 'email',
					'Value': email
				}
			]
		)

		users.createUser(username=username, role=role, email=email)

		return {'status': 200}
	# For member role: Create user, set password and then
	elif role == 'member':
		response = client.admin_create_user(
			UserPoolId = userPoolId,
			Username = username
		)
		# Set password to fixed thing
		# Randomly generate password and return value
		password = generateSecurePassword()

		response = client.admin_set_user_password(
		    UserPoolId=userPoolId,
		    Username=username,
		    Password=password,
		    Permanent=True
		)

		users.createUser(username=username, role=role, email=email)

		return {'status': 200, 'password': password}
	else:
		return {'status': 405}