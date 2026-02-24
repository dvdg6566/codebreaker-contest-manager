import os
import re
import boto3
import subprocess
from decimal import Decimal, InvalidOperation
from cmscmp import white_diff_step
from exec import execute, cleanProc

judgeName = os.environ['judgeName']
s3 = boto3.resource('s3')
submissions_bucket = s3.Bucket(f"{judgeName}-submissions")
testdata_bucket = s3.Bucket(f"{judgeName}-testdata")
checkers_bucket = s3.Bucket(f"{judgeName}-checkers")

# Deletes all tmp files (from previous invocations) at the start of an invocation
def deleteFiles():
	for file in os.listdir("/tmp"):
		os.unlink(file)

def lambda_handler(event, context):
	problemName = event["problemName"]
	subId = event["submissionId"]
	testcaseNumber = event["testcaseNumber"]
	language = event["language"]
	customChecker = event["customChecker"]
	timeLimit = float(event["timeLimit"]) # Time in s
	memoryLimit = float(event["memoryLimit"]) # Memory in MB

	os.chdir('/tmp')
	deleteFiles()
	cleanProc()
	
	INPUT_FILE = "input_file"
	OUTPUT_FILE = "output_file"
	if language == 'cpp':
		CODE_FILE = "code"
		cmd= f"ulimit -s unlimited; ./{CODE_FILE} < {INPUT_FILE}" # run cpp binary
		binaryPath = f"compiled/{subId}"
		submissions_bucket.download_file(binaryPath,CODE_FILE)
	elif language == 'py':
		CODE_FILE = "code.py"
		cmd = f"python3 {CODE_FILE} < {INPUT_FILE}" # run py file
		codePath = f"source/{subId}.py"
		submissions_bucket.download_file(codePath,CODE_FILE)

	# Download input testcase file and enable executable permissions to run
	inputPath = problemName + '/' + str(testcaseNumber) + '.in'
	testdata_bucket.download_file(inputPath,INPUT_FILE)
	subprocess.run(f"chmod +x {CODE_FILE}", shell=True)

	# Executes code and pipes output into comparison file
	result = execute(
		cmd = cmd,
		outputFile = 'comparison_file',
		timeLimit = timeLimit,
		memoryLimit = memoryLimit,
		checker=0
	) # File limit is input and output files
	
	# TLE, RTE, MLE
	if result['verdict'] != 'AC':
		return result
	
	outputPath = problemName + '/' + str(testcaseNumber) + '.out'
	testdata_bucket.download_file(outputPath,OUTPUT_FILE)
	
	if customChecker == 0:
		res = white_diff_step("comparison_file",OUTPUT_FILE)
		result['score'] = res
	else:
		checkers_bucket.download_file(f"compiled/{problemName}","checker")
		subprocess.run("chmod +x checker", shell=True)
		checkerCmd = f"ulimit -s unlimited; ./checker {INPUT_FILE} comparison_file {OUTPUT_FILE}" # run cpp file 
		
		# Executes checker with significantly more time
		checkerResult = execute(
			cmd = checkerCmd,
			outputFile = 'checker_out',
			timeLimit = 20,
			memoryLimit = 1024,
			checker=1
		)
		
		# Interpreting checker output
		try:
			with open("checker_out", "r") as f:
				checkerOutput = f.read()
			
			match = re.search(r'^\S+', checkerOutput)
			if match:
				scoreString = match.group(0)
			else:
				# If no space or newline, then Decimal entire score
				scoreString = checkerOutput
				
			score = Decimal(scoreString) * 100
			
			if score < 0 or score > 100: # Invalid Score
				result['verdict'] = 'CHECKER FAULT'
				result['score'] = 0
				return result
			result['score'] = round(score, 2)
		
		except Exception as e: # Invalid Output Format
			print(e)
			result['verdict'] = 'CHECKER FAULT'
			result['score'] = 0
			return result
	
	# Updates verdict based on score
	if result['score'] == 100:
		result['verdict'] = 'AC'
	elif result['score'] == 0:
		result['verdict'] = 'WA'
	else:
		result['verdict'] = 'PS'
	
	return result