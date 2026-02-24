import os
import json
import boto3
from decimal import *

judgeName = os.environ['judgeName']
region = os.environ['AWS_REGION']
accountId = os.environ['AWS_ACCOUNT_ID']

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
submissions_table = dynamodb.Table(f'{judgeName}-submissions')

def lambda_handler(event, context):
    subId = event["submissionId"]
    testcaseNumber = event["testcaseNumber"]
    
    response = lambda_client.invoke(
        FunctionName = f'arn:aws:lambda:{region}:{accountId}:function:{judgeName}-testcase-grader',
        InvocationType='RequestResponse',
        Payload = json.dumps(event)
    )
        
    result = json.loads(response['Payload'].read())

    result['score'] = Decimal(str(result['score']))
    response = submissions_table.update_item(
        Key = {'subId' : subId},
        UpdateExpression = f'set verdicts[{testcaseNumber}] = :verdict, times[{testcaseNumber}] = :time, memories[{testcaseNumber}]=:memory,score[{testcaseNumber}]=:score,returnCodes[{testcaseNumber}]=:returnCode,#st [{testcaseNumber}]=:status',
        ExpressionAttributeValues = {':verdict':result['verdict'],':time':Decimal(str(result['runtime'])), ':memory':Decimal(str(result['memory'])), ':score':result['score'], ':returnCode':result['returnCode'],':status':2},
        ExpressionAttributeNames = {'#st':'status'}
    )
    
    return result
