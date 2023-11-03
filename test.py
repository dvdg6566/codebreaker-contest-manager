from datetime import timedelta, datetime
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import awstools


print(awstools.sts.createRole(problemName = 'ping'))

# print(awstools.cognito.authenticate('test3', pw))

#a = awstools.submissions.checkSubmission('0rang3', 'addition', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))
#awstools.submissions.registerSubmission('0rang3', 'addition', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))
#b = awstools.submissions.checkSubmission('0rang3', 'hi', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))
#c = awstools.submissions.checkSubmission('0rang3', 'addition', datetime.utcnow(), awstools.problems.getProblemInfo('addition'))

#print(a,b,c)

# p = awstools.cognito.createUser('0rang3', 'admin')['password']
# print(awstools.cognito.authenticate('0rang3', p))
# print(p)

# print(awstools.contests.getAllContestTimes())

# p = awstools.cognito.resetPassword('0rang3')['password']
# print(p)
# print(awstools.cognito.authenticate('0rang3', p))
# print(awstools.cognito.resetPassword('0rang3'))

# print(p)