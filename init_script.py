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
		
	)
	
	# uploadFolder(
	# 	localPath = f'{filedir}/testdata',
	# 	bucket = f'{judgeName}-testdata',
	# 	s3path = 'ping'
	# )

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
	pass

if __name__ == '__main__':
	# createAddition()
	createPing()
	# createPrisoners()