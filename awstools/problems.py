import json
import boto3
from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')

judgeName = 'codebreaker'
accountId = '354145626860'
region = 'ap-southeast-1'

problems_table = dynamodb.Table(f'{judgeName}-problems')
STATEMENTS_BUCKET_NAME = f'{judgeName}-statements'
GRADERS_BUCKET_NAME = f'{judgeName}-graders'
CHECKERS_BUCKET_NAME = f'{judgeName}-checkers'
PROBLEM_VERIFICATION_LAMBDA_NAME = f'arn:aws:lambda:{region}:{accountId}:function:{judgeName}-problem-verification'
REGRADE_PROBLEM_LAMBDA_NAME = f'arn:aws:lambda:{region}:{accountId}:function:{judgeName}-regrade-problem'

def getAllProblems():
    results = awshelper.scan(problems_table)
    return results 
    
def getAllProblemNames():
    problemNames = awshelper.scan(problems_table, ProjectionExpression = 'problemName')
    return problemNames

def getAllProblemsLimited():
    return awshelper.scan(problems_table, 
        ProjectionExpression = 'problemName, analysisVisible, title, #source2, author, problem_type, noACs, validated, superhidden,createdTime,allowAccess',
        ExpressionAttributeNames={'#source2':'source'}
    )

def getProblemInfo(problemName):
    response= problems_table.query(
        KeyConditionExpression = Key('problemName').eq(problemName)
    )
    problem_info=response['Items']
    if len(problem_info) != 1:
        return None
    return problem_info[0]

def updateProblemInfo(problemName, info): 
    problems_table.update_item(
        Key = {'problemName' : problemName},
        UpdateExpression = f'set title=:a, #s=:b, author=:c, problem_type=:d, timeLimit=:e, memoryLimit=:f, fullFeedback=:g, customChecker=:h, attachments=:i',
        ExpressionAttributeValues={':a':info['title'], ':b':info['source'], ':c':info['author'], ':d':info['problem_type'], ':e':info['timeLimit'], ':f':info['memoryLimit'], ':g':info['fullFeedback'], ':h':info['customChecker'], ':i':info['attachments']},
        ExpressionAttributeNames={'#s':'source'}
    )

def makeAnalysisVisible(problemName):
    problems_table.update_item(
        Key = {'problemName' : problemName},
        UpdateExpression = f'set analysisVisible=:h',
        ExpressionAttributeValues={':h':1},
    )
    setSuperhidden(problemName, False)

def validateProblem(problemId):
    lambda_input = {'problemName':problemId}
    res = lambda_client.invoke(FunctionName = PROBLEM_VERIFICATION_LAMBDA_NAME, InvocationType='RequestResponse', Payload = json.dumps(lambda_input))

def createProblemWithId(problem_id):
    info = {}
    info['title'] = problem_id
    info['source'] = 'Unknown Source'
    info['author'] = ''
    info['problem_type'] = 'Batch'
    info['timeLimit'] = 1
    info['memoryLimit'] = 1024
    info['fullFeedback'] = True
    info['analysisVisible'] = False
    info['customChecker'] = False
    info['attachments'] = False
    info['testcaseCount'] = 0
    updateProblemInfo(problem_id, info)
    subtasks = {}
    subtasks['subtaskScores'] = []
    subtasks['subtaskDependency'] = []
    subtasks['subtaskScores'].append(100)
    subtasks['subtaskDependency'].append('1')
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
