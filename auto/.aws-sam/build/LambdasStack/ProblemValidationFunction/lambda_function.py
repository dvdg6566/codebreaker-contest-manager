import re
import os
import awstools

judgeName = os.environ['judgeName']
STATEMENTS_BUCKET = f'{judgeName}-statements'
CHECKERS_BUCKET = f'{judgeName}-checkers'
ATTACHMENTS_BUCKET = f'{judgeName}-attachments'
GRADERS_BUCKET = f'{judgeName}-graders'

def verifyDependency(dependency,memo):
	ranges = dependency.split(',')
	ans = 0
	for i in ranges:
		nums = i.split('-')
		if len(nums) > 1:
			x, y = int(nums[0]), int(nums[1])
			for i in range(x,y+1):
				if i < len(memo): memo[i]=1
			ans=max(ans,y)
		else:
			x = int(nums[0])
			ans=max(ans,x)
			if x < len(memo): memo[x]=1
	return ans

def lambda_handler(event, context):
	problemName = event['problemName']

	remarks= {
		'testdata': 'Ok',
		'attachments': 'Ok, no attachments required',
		'checker': 'Ok, no checker required',
		'statement': 'Ok',
		'grader': 'Ok, no grader required',
		'subtasks': 'Ok',
		'scoring': 'Ok'
	}
	verdicts={
		'testdata': 1,
		'attachments' : 1,
		'checker': 1,
		'statement': 1,
		'grader': 1,
		'subtasks': 1,
		'scoring': 1
	}
	
	problemInfo = awstools.getProblemInfo(problemName)
	
	# Verifying statements
	hasHTML = awstools.hasFile(STATEMENTS_BUCKET, f'{problemName}.html')
	hasPDF = awstools.hasFile(STATEMENTS_BUCKET, f'{problemName}.pdf')
	
	if hasHTML and hasPDF:
		remarks['statement'] = 'Ok, Both PDF and HTML statements found!'
	elif hasHTML:
		remarks['statement'] = 'Ok, HTML statement found!'
	elif hasPDF:
		remarks['statement'] = 'Ok, PDF statement found!'
	else:
		remarks['statement'] = 'No statement found!'
		verdicts['statement'] = 0
	
	# Verifying checker
	if problemInfo['customChecker'] == 1:
		if awstools.hasFile(CHECKERS_BUCKET, f'compiled/{problemName}'):
			remarks['checker'] = 'Ok, checker found!'
		else:
			remarks['checker'] = 'No checker found!'
			verdicts['checker'] = 0
		
	# Verifying attachments
	if problemInfo['attachments'] == 1:
		if awstools.hasFile(ATTACHMENTS_BUCKET, f'{problemName}.zip'):
			remarks['attachments'] = 'Ok, attachments found!'
		else:
			remarks['attachments'] = 'No attachments found!'
			verdicts['attachments'] = 0
		
	# Verifying grader
	if problemInfo['problem_type'] != 'Batch':
		hasHeader = True
		hasGrader = awstools.hasFile(GRADERS_BUCKET, f'{problemName}/grader.cpp')
		
		if problemInfo['problem_type'] == 'Interactive':
			if not awstools.hasFile(GRADERS_BUCKET, f'{problemName}/{problemName}.h'):
				hasHeader = False
		
		elif problemInfo['problem_type'] == 'Communication':
			if not (awstools.hasFile(GRADERS_BUCKET, f"{problemName}/{problemInfo['nameA']}.h" or awstools.hasFile(GRADERS_BUCKET, f"{problemName}/{problemInfo['nameB']}.h"))):
				hasHeader = False
		
		if hasGrader and hasHeader:
			remarks['grader'] = 'Ok, both header and grader file found!'
		elif hasGrader:
			remarks['grader'] = 'No header file found!'
			verdicts['grader'] = 0
		elif hasHeader:
			remarks['grader'] = 'No grader found!'
			verdicts['grader'] = 0
		else:
			remarks['grader'] = 'No grader and header file found!'
			verdicts['grader'] = 0
	
	# Checking score
	totalScore = 0 
	remarks['scoring'] = f'Ok, total score is 100!'
	for i in problemInfo['subtaskScores']:
		if i < 0:
			remarks['scoring'] = f'Subtask score cannot be negative!'
			verdicts['scoring'] = 0
		totalScore += i
	if totalScore != 100:
		remarks['scoring'] = f'Total Score is {totalScore}!'
		verdicts['scoring'] = 0
		
	# Checking subtasks
	testcaseFiles = awstools.getTestcaseFiles(prefix = f'{problemName}/')
	testcaseCount = 0
	maxValue = 0
	filenames = []

	for obj in testcaseFiles:
		filename = obj.key

		# Invalid file name
		validFileName = re.match('^[\w]+/[\d]+\.(in|out)$', filename)
		if validFileName == None: continue

		# Split by / to remove the folder name, split '.' to separate in and out
		x = filename.split('/')[1].split('.')
		if x[0] == '':
			continue
		filenames.append(x)			
		testcaseCount += 1
	# Each testcase should have in and out files
	testcaseCount = int(testcaseCount/2) 

	memo = [0 for i in range(testcaseCount+1)]
	# VERIFYING SUBTASK DEPENDENCY
	for i in problemInfo['subtaskDependency']:
		maxValue = max(maxValue,verifyDependency(i,memo))
		# Passing memo in as a pointer (python passess objects by reference)
	if maxValue > testcaseCount:
		remarks['subtasks'] = f'Subtasks reflect {maxValue} testcases while there are {testcaseCount} testcases!'
		verdicts['subtasks'] = 0
	elif sum(memo) != testcaseCount:
		fail = -1
		for i in range(1,testcaseCount+1):
			if not memo[i]: 
				fail = i
				break
		remarks['subtasks'] = f'Testcase {fail} not in any subtask!'
		verdicts['subtasks'] = 0
	
	# Checking testdata
	validation = [[0,0] for i in range(testcaseCount)]
	numFail = 0
	
	for x in filenames:
		ind = int(x[0])-1
		if ind>=testcaseCount:continue
		if(x[1] == 'in'):
			validation[ind][0]=1
		else:
			validation[ind][1]=1
	
	firstFail = ''
	for i in range(testcaseCount):
		if validation[i][0] == 0:
			if numFail == 0:
				firstFail = f'{i+1}.in'
			numFail += 1
		if validation[i][1] == 0:
			if numFail == 0:
				firstFail = f'{i+1}.out'
			numFail += 1
			
	if numFail:
		verdicts['testdata'] = 0
		remarks['testdata'] = f'{numFail} testcases missing, including file {firstFail}!'
	else:
		remarks['testdata'] = f'Ok, {testcaseCount} testcases found!'
		
	validated = 1
	for i in verdicts.keys():
		if verdicts[i] != 1: validated = 0
	
	awstools.updateResults(problemName, validated, verdicts, remarks, testcaseCount)
	
	return {
		'statusCode':200,
		'verdicts':verdicts,
		'remarks':remarks
	}

