# Manages authentication and logins
import os
import boto3
import string
import secrets
from awstools import users
from botocore.exceptions import ClientError

userPoolId = os.environ.get('COGNITO_USER_POOL_ID')
clientId = os.environ.get('COGNITO_CLIENT_ID')
client = boto3.client('cognito-idp')

def generateSecurePassword():
	# Generates secure password to set when creating member accounts
	alphabet = string.ascii_letters + string.digits + string.punctuation
	
	# Remove inverted commas 
	alphabet = alphabet.replace('\'', '')
	alphabet = alphabet.replace('\"', '')
	
	alphanum = string.ascii_letters + string.digits

	# First and last character of password should not have punctuation (QoL improvement)
	password = secrets.choice(alphanum) + ''.join(secrets.choice(alphabet) for i in range(6)) + secrets.choice(alphanum)
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

def createUser (username, role):
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

	users.createUser(username=username, role=role)

	return {'status': 200, 'password': password}

def resetPassword (username):
	password = generateSecurePassword()

	response = client.admin_set_user_password(
	    UserPoolId=userPoolId,
	    Username=username,
	    Password=password,
	    Permanent=True
	)

	return {'status': 200, 'password': password}