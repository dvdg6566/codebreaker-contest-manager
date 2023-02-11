import os
import json
import boto3
from awstools import awshelper
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')
SFclient = boto3.client('stepfunctions')

judgeName = os.environ.get('JUDGE_NAME')
accountId = os.environ.get('AWS_ACCOUNT_ID')
region = os.environ.get('AWS_REGION')

problems_table = dynamodb.Table(f'{judgeName}-problems')
STATEMENTS_BUCKET_NAME = f'{judgeName}-statements'
GRADERS_BUCKET_NAME = f'{judgeName}-graders'
CHECKERS_BUCKET_NAME = f'{judgeName}-checkers'
TESTDATA_BUCKET_NAME = f'{judgeName}-testdata'
PROBLEM_VALIDATION_LAMBDA_NAME = f'arn:aws:lambda:{region}:{accountId}:function:{judgeName}-problem-validation'
REGRADE_PROBLEM_LAMBDA_NAME = f'arn:aws:lambda:{region}:{accountId}:function:{judgeName}-regrade-problem'

def getAllProblems():
    results = awshelper.scan(problems_table)
    return results 
    
def getAllProblemNames():
    res = awshelper.scan(problems_table, ProjectionExpression = 'problemName')
    return [i['problemName'] for i in res]

def getAllProblemsLimited():
    return awshelper.scan(problems_table, 
        ProjectionExpression = 'problemName, title, problem_type, validated',
    )

def getProblemInfo(problemName):
    response = problems_table.get_item(
        Key={ "problemName": problemName }
    )
    if 'Item' not in response.keys(): return None
    return response['Item']

def updateProblemInfo(problemName, info): 
    problems_table.update_item(
        Key = {'problemName' : problemName},
        UpdateExpression = f'set title=:a, problem_type=:b, timeLimit=:c, memoryLimit=:d, attachments=:e, customChecker=:f, fullFeedback=:g',
        ExpressionAttributeValues={':a':info['title'], ':b':info['problem_type'], ':c':info['timeLimit'], ':d':info['memoryLimit'], ':e':info['attachments'], ':f':info['customChecker'], ':g':info['fullFeedback']},
    )

def validateProblem(problemName):
    lambda_input = {'problemName':problemName}
    res = lambda_client.invoke(FunctionName = PROBLEM_VALIDATION_LAMBDA_NAME, InvocationType='RequestResponse', Payload = json.dumps(lambda_input))
    return res

def createProblemWithId(problem_id):
    info = {}
    info['title'] = problem_id
    info['problem_type'] = 'Batch'
    info['timeLimit'] = 1
    info['memoryLimit'] = 1024
    info['attachments'] = False
    info['customChecker'] = False
    info['fullFeedback'] = True
    info['testcaseCount'] = 0
    updateProblemInfo(problem_id, info)
    subtasks = {}
    subtasks['subtaskScores'] = [100]
    subtasks['subtaskDependency'] = ['1']
    updateSubtaskInfo(problem_id, subtasks)
    validateProblem(problem_id)

def updateCommunicationFileNames(problemName, info):
    problems_table.update_item(
        Key = {'problemName' : problemName},
        UpdateExpression = f'set nameA=:a, nameB=:b',
        ExpressionAttributeValues = {':a':info['nameA'], ':b':info['nameB']}
    )

def deleteStatement(statementName):
    s3.delete_object(Bucket=STATEMENTS_BUCKET_NAME, Key=statementName)

def uploadStatement(statement, s3Name):
    s3.upload_fileobj(statement, STATEMENTS_BUCKET_NAME, s3Name, ExtraArgs={"ContentType":statement.content_type})

def updateCount(problemName):
    lambda_input = {"problemName": problemName}
    res = lambda_client.invoke(FunctionName = 'arn:aws:lambda:ap-southeast-1:354145626860:function:codebreaker-update-testcaseCount', InvocationType='RequestResponse', Payload = json.dumps(lambda_input))

def updateSubtaskInfo(problemName, info):
    problems_table.update_item(
        Key = {'problemName' : problemName},
        UpdateExpression = f'set subtaskScores=:a, subtaskDependency=:b',
        ExpressionAttributeValues={':a':info['subtaskScores'], ':b':info['subtaskDependency']}
    )

def updateEditorialInfo(problemName, info):
    problems_table.update_item(
        Key = {'problemName': problemName},
        UpdateExpression = f'set editorials=:a',
        ExpressionAttributeValues = {':a':info['editorials']}
    )

def uploadCompiledChecker(sourceName, uploadTarget):
    s3.upload_file(sourceName, CHECKERS_BUCKET_NAME, uploadTarget)

def uploadGrader(sourceName, uploadTarget):
    s3.upload_fileobj(sourceName, GRADERS_BUCKET_NAME, uploadTarget)

# ADMINS CAN DOWNLOAD TESTDATA IN PROBLEM VIEW PAGE
def getTestcase(path):
    tcfile = s3.get_object(Bucket=TESTDATA_BUCKET_NAME, Key=path)
    body = tcfile['Body'].read().decode("utf-8")
    return body

# GET ATTACHMENT IN PROBLEM VIEW PAGE
def getAttachment(path):
    attachment = s3.get_object(Bucket=ATTACHMENTS_BUCKET_NAME, Key=path)
    # No need to decode object because attachments are zip files
    return attachment['Body']

# GENERATES PROBLEM STATEMENT HTML (FOR BOTH PDF AND HTML)
def getProblemStatementHTML(problemName):
    statement = ''
    try:
        htmlfile = s3.get_object(Bucket=STATEMENTS_BUCKET_NAME, Key=f'{problemName}.html') 
        body = htmlfile['Body'].read().decode("utf-8") 
        statement += body
    except s3.exceptions.NoSuchKey as e:
        pass
    try:
        name = f'{problemName}.pdf'
        s3.head_object(Bucket=STATEMENTS_BUCKET_NAME, Key=name)
        if (len(statement) > 0):
            statement += '<br>'
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': STATEMENTS_BUCKET_NAME, 'Key': name},
            ExpiresIn=60)

        statement += '<iframe src=\"' + url + '\" width=\"100%\" height=\"700px\"></iframe>'
    except ClientError as e:
        pass
    if (len(statement) == 0):
        return {'status': 404, 'response':'No statement is currently available'}
    else:
        return {'status': 200, 'response':statement}

# REGRADE PROBLEM AS INVOKED IN ADMIN PAGE
# Regrade type can be NORMAL, AC, NONZERO
def regradeProblem(problemName, regradeType = 'NORMAL'): 

    # Stitching is always on
    stitch = 1

    lambda_input = {
        'problemName': problemName,
        'regradeType': regradeType,
        'stitch': stitch
    }

    res = lambda_client.invoke(FunctionName = REGRADE_PROBLEM_LAMBDA_NAME, InvocationType='Event', Payload = json.dumps(lambda_input))    

''' END: GRADING '''