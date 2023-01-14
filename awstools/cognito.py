# Manages authentication and logins
import boto3
from botocore.exceptions import ClientError

client = boto3.client('cognito-idp')

def authenticate(username, password):
	try:
		response = client.initiate_auth(
			AuthFlow = 'USER_PASSWORD_AUTH',
			AuthParameters = {
				"USERNAME" : username,
		      	"PASSWORD" : password
			},
			ClientId = "30ie37hitd97h3nge5uhf4kodp"
		)
		
		return {'status': 200, 'username': username}
		
	except ClientError as e:
		if e.response['Error']['Code'] == 'NotAuthorizedException':
			return {'status': 403}
		else:
			return {'status':400}