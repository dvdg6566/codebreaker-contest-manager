from datetime import timedelta, datetime
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import awstools

# awstools.users.setContest(['sgzoo', 'sgzoo2'], 'firstcontest')

# print(awstools.cognito.generateSecurePassword())
# awstools.cognito.createUser('0rang3', 'admin', email='czhdaniel@gmail.com')
# resp = awstools.cognito.createUser('test3', 'member')
# pw = resp['password']
# pw = "3'K*V..Z"
# print(resp)

# print(awstools.cognito.authenticate('test3', pw))

#a = awstools.submissions.checkSubmission('0rang3', 'addition', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))
#awstools.submissions.registerSubmission('0rang3', 'addition', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))
#b = awstools.submissions.checkSubmission('0rang3', 'hi', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))
#c = awstools.submissions.checkSubmission('0rang3', 'addition', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))

#print(a,b,c)