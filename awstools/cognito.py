# Manages authentication and logins
import os
import boto3
import string
import secrets
from awstools import users
from botocore.exceptions import ClientError

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
		if e.response['Error']['Code'] == 'NotAuthorizedException':
			return {'status': 403}
		else:
			return {'status':400}

def createUser (username, email, role):
	# For admin role: Create user and let cognito send email
	if role == 'admin':
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
	# For member role: Create user, set password and then
	elif role == 'member':
		response = client.admin_create_user(
			UserPoolId = 'ap-southeast-1_xiTNBPfQ3',
			Username = username
		)
		# Set password to fixed thing
		# Randomly generate password and return value
		password = generateSecurePassword()

		response = client.admin_set_user_password(
		    UserPoolId='ap-southeast-1_xiTNBPfQ3',
		    Username=username,
		    Password='P@55w0rd',
		    Permanent=True
		)
	else:
		return {'status': 405}

	users.createUser(username, email, role)