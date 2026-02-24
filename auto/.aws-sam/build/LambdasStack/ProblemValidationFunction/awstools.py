import os
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

judgeName = os.environ['judgeName']
accountId = os.environ['AWS_ACCOUNT_ID']

s3=boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')
problems_table = dynamodb.Table(f'{judgeName}-problems')

testdata_bucket = s3.Bucket(f'{judgeName}-testdata')
lambda_client = boto3.client('lambda')

def testcaseCount(problemName):
    problemName = event['problemName']
    testcaseCount = 0

    for obj in testdata_bucket.objects.filter(Prefix="{0}/".format(problemName)):
        testcaseCount += 1

    return testcaseCount

def getProblemInfo(problemName):
    response = problems_table.query(
        KeyConditionExpression = Key('problemName').eq(problemName)
    )
    problem_info=response['Items']
    if len(problem_info) != 1:
        return None
    return problem_info[0]

def hasFile(bucket, filepath):
	try:
		s3.Object(bucket, filepath).load()
		return True
	except ClientError as e:
		return False

def getTestcaseFiles(prefix):
	return testdata_bucket.objects.filter(Prefix=prefix)

def updateResults(problemName, validated, verdicts, remarks, testcaseCount):
	problems_table.update_item(
		Key = {'problemName':problemName},
		UpdateExpression = f'set validated=:a,verdicts=:b,remarks=:c,testcaseCount=:d',
		ExpressionAttributeValues={':a':validated,':b':verdicts,':c':remarks,':d':testcaseCount}
	)
