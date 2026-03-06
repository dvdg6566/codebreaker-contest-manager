import awstools
import subprocess
from compilesub import format

def compileChecker(problemName):
	sourceName = f"{problemName}.cpp"
	compiledName = f"{problemName}"
	sourceS3Path = f"source/{problemName}.cpp"
	compiledS3Path = f"compiled/{problemName}"

	# Get source file
	awstools.getChecker(s3path = sourceS3Path, localpath = sourceName)
	subprocess.run(f"chmod +x {sourceName}", shell=True)

	cmd=f"timeout 30s g++ -O2 -o {compiledName} {sourceName} -m64 -static -std=gnu++17 -lm -s -w -Wall -Wshadow -fmax-errors=512" 

	try:
		process = subprocess.run(cmd, shell=True, capture_output=True)
		process.check_returncode()

		#Upload the compiled code to S3
		awstools.uploadCompiledChecker(localpath=compiledName,s3path=compiledS3Path)

		return {'status':200, 'error':''}
	except subprocess.CalledProcessError:
		compileError = format(process.stderr.decode('UTF-8'), problemName = problemName)
		
		# Return 422 unprocessable entity for compile errors
		return {'status':422,'error':compileError}