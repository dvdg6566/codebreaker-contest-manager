import os
import subprocess

# Loads environment variables using dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

judgeName = os.environ.get('JUDGE_NAME')

import awstools

# This should be run form github root

def uploadFile(localPath, bucket, s3path):
	cmd = f'aws s3 cp {localPath} s3://{bucket}/{s3path}'
	subprocess.run(cmd, shell=True)

def uploadFolder(localPath, bucket, s3path):
	cmd = f'aws s3 cp {localPath} s3://{bucket}/{s3path} --recursive'
	subprocess.run(cmd, shell=True)

def validateProblem(problemName):
	print("Validating Problem")
	val = awstools.problems.validateProblem(problemName=problemName)

	verdicts = val['verdicts']

	if min([verdicts[i] for i in verdicts]) == 1:
		print("Validation Success!")
	else:
		print("Validation Failure!")
		for i in verdicts: 
			if verdicts[i] == 0: print(f'Category {i}: {val["remarks"][i]}')

def createAddition():
	filedir = f'init/problems/addition'
	print("Creating problem named addition")
	awstools.problems.createProblemWithId(problemName = 'addition')

	print("Uploading files")
	uploadFile(
		localPath = f'{filedir}/statement.html',
		bucket = f'{judgeName}-statements',
		s3path = 'addition.html'
	)

	uploadFolder(
		localPath = f'{filedir}/testdata',
		bucket = f'{judgeName}-testdata',
		s3path = 'addition'
	)

	print("Updating Subtasks")
	awstools.problems.updateSubtaskInfo(
		problemName = 'addition',
		info = {
			'subtaskScores': [0, 36, 64],
			'subtaskDependency': ['1', '1-3', '1-4']
		}
	)

	validateProblem(problemName = 'addition')

def createPing():
	filedir = f'init/problems/ping'
	print("Creating problem named ping")
	awstools.problems.createProblemWithId(problemName = 'ping')

	print("Uploading files")
	uploadFile(
		localPath = f'{filedir}/statement.pdf',
		bucket = f'{judgeName}-statements',
		s3path = 'ping.pdf'
	)

	uploadFile(
		localPath = f'{filedir}/attachments.zip',
		bucket = f'{judgeName}-attachments',
		s3path = 'ping.zip'
	)

	uploadFile(
		localPath = f'{filedir}/checker.cpp',
		bucket = f'{judgeName}-checkers',
		s3path = 'source/ping.cpp'
	)

	uploadFile(
		localPath = f'{filedir}/grader.cpp',
		bucket = f'{judgeName}-graders',
		s3path = 'ping/grader.cpp'
	)

	uploadFile(
		localPath = f'{filedir}/ping.h',
		bucket = f'{judgeName}-graders',
		s3path = 'ping/ping.h'
	)

	uploadFolder(
		localPath = f'{filedir}/testdata',
		bucket = f'{judgeName}-testdata',
		s3path = 'ping'
	)

	print("Compiling Checker")
	res = awstools.problems.compileChecker(
		problemName = 'ping'
	)

	if res['status'] == 200:
		print("Checker compilation success!")
	else:
		if 'error' in res: print(res['error'])

	problemInfo = awstools.problems.getProblemInfo(problemName = 'ping')
	
	problemInfo['customChecker'] = True
	problemInfo['problem_type'] = 'Interactive'
	problemInfo['attachments'] = True

	awstools.problems.updateProblemInfo(
		problemName = 'ping',
		info = problemInfo
	)

	print("Updating Subtasks")
	awstools.problems.updateSubtaskInfo(
		problemName = 'ping',
		info = {
			'subtaskScores': [10, 30, 60],
			'subtaskDependency': ['1-20', '1-73', '74-152']
		}
	)

	validateProblem(problemName = 'ping')

def createPrisoners():
	filedir = f'init/problems/prisoners'
	print("Creating problem named prisoners")
	awstools.problems.createProblemWithId(problemName = 'prisoners')

	print("Uploading files")
	uploadFile(
		localPath = f'{filedir}/statement.pdf',
		bucket = f'{judgeName}-statements',
		s3path = 'prisoners.pdf'
	)

	uploadFile(
		localPath = f'{filedir}/attachments.zip',
		bucket = f'{judgeName}-attachments',
		s3path = 'prisoners.zip'
	)

	uploadFile(
		localPath = f'{filedir}/checker.cpp',
		bucket = f'{judgeName}-checkers',
		s3path = 'source/prisoners.cpp'
	)

	uploadFile(
		localPath = f'{filedir}/grader.cpp',
		bucket = f'{judgeName}-graders',
		s3path = 'prisoners/grader.cpp'
	)

	uploadFile(
		localPath = f'{filedir}/prisoner.h',
		bucket = f'{judgeName}-graders',
		s3path = 'prisoners/prisoner.h'
	)

	uploadFile(
		localPath = f'{filedir}/swapper.h',
		bucket = f'{judgeName}-graders',
		s3path = 'prisoners/swapper.h'
	)

	uploadFolder(
		localPath = f'{filedir}/testdata',
		bucket = f'{judgeName}-testdata',
		s3path = 'prisoners'
	)

	print("Compiling Checker")
	res = awstools.problems.compileChecker(
		problemName = 'prisoners'
	)

	if res['status'] == 200:
		print("Checker compilation success!")
	else:
		if 'error' in res: print(res['error'])

	problemInfo = awstools.problems.getProblemInfo(problemName = 'prisoners')
	
	problemInfo['customChecker'] = True
	problemInfo['problem_type'] = 'Communication'
	problemInfo['attachments'] = True

	awstools.problems.updateProblemInfo(
		problemName = 'prisoners',
		info = problemInfo
	)

	awstools.problems.updateCommunicationFileNames(
		problemName = 'prisoners',
		info = {'nameA': 'swapper', 'nameB': 'prisoner'}
	)

	print("Updating Subtasks")
	awstools.problems.updateSubtaskInfo(
		problemName = 'prisoners',
		info = {
			'subtaskScores': [27, 29, 44, 0],
			'subtaskDependency': ['1-10', '11-20', '1-30', '31']
		}
	)

	validateProblem(problemName = 'prisoners')

def createDefaultAdmin():
	try:
		awstools.cognito.createUser(
			username = 'admin',
			password = 'P@55w0rd',
			role = 'admin'
		)
		print("Admin credentials created admin:complex")
	except Exception as e:
		awstools.cognito.resetPassword(
			username = 'admin',
			password = 'P@55w0rd'
		)
		print("Admin password reset to complex!")

if __name__ == '__main__':
	createDefaultAdmin()
	createAddition()
	createPing()
	createPrisoners()
	# pass