import awstools
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# print(awstools.cognito.generateSecurePassword())
awstools.cognito.createUser('0rang3', 'admin', email='czhdaniel@gmail.com')
# resp = awstools.cognito.createUser('test3', 'member')
# pw = resp['password']
# pw = "3'K*V..Z"
# print(resp)

# print(awstools.cognito.authenticate('test3', pw))