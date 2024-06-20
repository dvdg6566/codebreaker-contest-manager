import awstools
from decimal import Decimal

def lambda_handler(event, context):
	problemName = event['problemName']
	subId = event['submissionId']
	username = event['username']
	compileError = event['compileError']
	compileErrorMessage = event['compileErrorMessage']
	
	# When there is a compile error, we do not need to update any scores.
	# Just update the compile error message in Dynamo

	if compileError:
		awstools.updateCE(
			subId=subId, 
			compileErrorMessage=compileErrorMessage
		)
		return {'status':200}

	problemInfo = awstools.getProblemInfo(problemName)        

	subtaskDependency = problemInfo['subtaskDependency']
	subtaskTotalScores = problemInfo['subtaskScores']
	testcaseCount = int(problemInfo['testcaseCount'])
	subtaskCount = len(subtaskDependency)
	subtaskScores = [0 for i in range(subtaskCount)]

	submissionInfo = awstools.getSubmission(subId=subId)
	scores = submissionInfo['score'] # List of scores for each testcase
	submissionTime = submissionInfo['submissionTime']

	maxTime = max(submissionInfo['times']) # Maximum runtime across testcases
	maxMemory = max(submissionInfo['memories']) # Maximum memory across testcases
	
	''' BEGIN: EVALUATE CURRENT SUBMISSION '''
	
	def calculateSubtaskScores(subtaskDependency, scores):
		subtaskScores = [100 for i in range(subtaskCount)]
		for i in range(subtaskCount):
			dep = subtaskDependency[i].split(',')
			for t in dep:
				x = t.split('-')
				if(len(x) == 1): # Dependency has single testcase
					ind = int(x[0])
					subtaskScores[i] = min(subtaskScores[i], scores[ind])
				elif len(x) == 2: # Dependency has range of testcases
					st = int(x[0])
					en = int(x[1])
					for j in range(st,en+1):
						subtaskScores[i] = min(subtaskScores[i], scores[j])
		return subtaskScores
	
	# Subtask Scores is the score for the latest submission
	subtaskScores = calculateSubtaskScores(subtaskDependency, scores)
	 
	totalScore = 0
	for i in range(subtaskCount):
		totalScore += subtaskScores[i] * subtaskTotalScores[i]

	totalScore = Decimal(round(totalScore/100, 2))

	awstools.updateSubmission(
		subId = subId, 
		maxTime = maxTime, 
		maxMemory = maxMemory, 
		subtaskScores = subtaskScores,
		totalScore = totalScore
	)
	''' END: EVALUATE CURRENT SUBMISSION ''' 

	''' BEGIN: STITCHING FOR USER'S MAXIMUM SCORE '''
	submissions = awstools.getStitchSubmissions(
		username=username, problemName=problemName
	)
	
	# Subtask Max Scores is the maximum score across all old submissions
	subtaskMaxScores = [0] * subtaskCount
	
	# Iterate through all old submissions and find maximum score for each subtask	
	for oldSub in submissions:
		# Invalid submission (different number of TC)
		# -1 because scores is 1-indexed
		if len(oldSub['score']) - 1 != testcaseCount: continue 
		for subtask in range(subtaskCount):
			subtaskMaxScores[subtask] = max(subtaskMaxScores[subtask], oldSub['subtaskScores'][subtask])

	# Calculate score based on old submissions score 
	stitchedScore = 0
	for i in range(subtaskCount):
		stitchedScore += max(subtaskScores[i], subtaskMaxScores[i]) * subtaskTotalScores[i]
	stitchedScore = Decimal(round(stitchedScore/100, 2))

	# Update user table if score is updated
	userInfo = awstools.getProblemScores(username)
	problemScore = 0
	if problemName in userInfo['problemScores']:
		problemScore = userInfo['problemScores'][problemName]

	if stitchedScore > problemScore:
		# Update latest score change
		awstools.updateUserScore(
			username = username, 
			problemName = problemName, 
			stitchedScore = stitchedScore,
			latestScoreChange = submissionTime
		)
	
	''' END: STITCHING FOR USER'S MAXIMUM SCORE  '''
	return {
		"statusCode":200
	}
