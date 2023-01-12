# Manages authentication and logins
import boto3

client = boto3.client('cognito-idp')

def getUserInfo(accessToken):
	response = client.get_user(AccessToken = accessToken)
	username = response['Username']
	return username