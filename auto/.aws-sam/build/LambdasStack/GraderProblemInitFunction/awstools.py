import os
import boto3

judgeName = os.environ['judgeName']
dynamodb = boto3.resource('dynamodb','ap-southeast-1')
problems_table = dynamodb.Table('codebreaker-problems')
submissions_table = dynamodb.Table(f'{judgeName}-submissions')

def uploadSubmission(submission_upload):
    submissions_table.put_item(Item = submission_upload)

def getProblemInfo(problemName):
    response = problems_table.get_item(
        Key={ "problemName": problemName }
    )
    if 'Item' not in response.keys(): return None
    return response['Item']