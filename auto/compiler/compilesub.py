import awstools
import subprocess

# MAXIMUM LENGTH OF COMPILE ERROR ERROR MESSAGE
MAX_ERROR_LENGTH = 1000

''' HELP TO FORMAT COMPILE ERROR TO BE VIEWED IN HTML '''
def format(compileError, problemName):
	compileError = compileError.replace(f"tmp/{problemName}", problemName)
	# Format compile error for display in HTML
	compileError = compileError.replace("<", "&lt;")
	compileError = compileError.replace(">", "&gt;")
	compileError = compileError.replace("\n", "<br>")
	compileError = compileError[:MAX_ERROR_LENGTH]
	if compileError == "":
		compileError = 'Compile timed out after 30s'
	return compileError

def compileBatch(submissionId, problemName, grader, language):
	sourceName = f"{problemName}.cpp"
	compiledName = f"{problemName}"
	sourceS3Path = f"source/{submissionId}.cpp"
	compiledS3Path = f"compiled/{submissionId}"

	# Get source file
	awstools.getSubmission(s3path = sourceS3Path, localpath = sourceName)

	cmd=f"timeout 30s g++ -O2 -o {compiledName} {sourceName} -m64 -static -std=gnu++17 -lm -s -w -Wall -Wshadow -fmax-errors=512" 

	try:
		process = subprocess.run(cmd, shell=True, capture_output=True)
		process.check_returncode()

		#Upload the compiled code to S3
		awstools.uploadCode(localpath=compiledName,s3path=compiledS3Path)

		return {'status':200, 'error':''}
	except subprocess.CalledProcessError:
		compileError = format(process.stderr.decode('UTF-8'), problemName = problemName)
		
		# Return 422 unprocessable entity for compile errors
		return {'status':422,'error':compileError}

def compileInteractive(submissionId, problemName, grader, language):
	sourceName = f"{problemName}.cpp"
	headerName = f"{problemName}.h"
	graderName = "grader.cpp"
	compiledName = f"{problemName}"
	sourceS3Path = f"source/{submissionId}.cpp"
	compiledS3Path = f"compiled/{submissionId}"

	awstools.getGraderFile(s3path=f'{problemName}/grader.cpp',localpath=graderName)
	awstools.getGraderFile(s3path=f'{problemName}/{problemName}.h',localpath=headerName)
	awstools.getSubmission(s3path = sourceS3Path, localpath = sourceName)

	cmd=f"timeout 30s g++ -O2 -o {compiledName} {graderName} {sourceName} -m64 -static -std=gnu++17 -lm -s -w -Wall" 

	try:
		process = subprocess.run(cmd, shell=True, capture_output=True)
		process.check_returncode()
		
		#Upload the compiled code to S3
		awstools.uploadCode(localpath=compiledName,s3path=compiledS3Path)

		return {'status': 200, 'error':''}
	except subprocess.CalledProcessError as e:
		compileError = format(process.stderr.decode('UTF-8'), problemName = problemName)

		return {'status':422,'error':compileError}

def compileCommunication(submissionId, problemName, grader, language):
	problemInfo = awstools.getCommunicationFileNames(problemName=problemName)
	nameA = problemInfo['nameA']
	nameB = problemInfo['nameB']

	sourceAName = f"{nameA}.cpp"
	sourceBName = f"{nameB}.cpp"
	headerAName = f"{nameA}.h"
	headerBName = f"{nameB}.h"
	graderName = "grader.cpp"
	compiledName = f"{problemName}"
	sourceAS3Path = f"source/{submissionId}A.cpp"
	sourceBS3Path = f"source/{submissionId}B.cpp"
	compiledS3Path = f"compiled/{submissionId}"

	# Bring submission files and grader files to local
	awstools.getSubmission(s3path=sourceAS3Path, localpath=sourceAName)
	awstools.getSubmission(s3path=sourceBS3Path, localpath=sourceBName)
	awstools.getGraderFile(s3path=f'{problemName}/grader.cpp', localpath=graderName)
	awstools.getGraderFile(s3path=f'{problemName}/{nameA}.h', localpath=headerAName)
	awstools.getGraderFile(s3path=f'{problemName}/{nameB}.h', localpath=headerBName)

	try:
		#compile the code
		cmd=f"timeout 30s g++ -O2 -o {compiledName} {graderName} {sourceAName} {sourceBName} -m64 -static -std=gnu++17 -lm -s -w -Wall" 

		process = subprocess.run(cmd, shell=True, capture_output=True)
		process.check_returncode()
		
		#Upload the compiled binary to S3
		awstools.uploadCode(localpath=compiledName,s3path=compiledS3Path)
		
		return {'status': 200, 'error':''}
	except subprocess.CalledProcessError as e:
		compileError = format(process.stderr.decode('UTF-8'), problemName = problemName)

		return {'status':422,'error':compileError}
