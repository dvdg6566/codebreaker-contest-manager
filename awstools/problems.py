import boto3
from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')

judgeName = 'codebreaker'
problems_table = dynamodb.Table(f'{judgeName}-problems')
STATEMENTS_BUCKET_NAME = 'codebreaker-statements'
GRADERS_BUCKET_NAME = 'codebreaker-graders'
CHECKERS_BUCKET_NAME = 'codebreaker-checkers'

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
        UpdateExpression = f'set title=:a, #s=:b, author=:c, problem_type=:d, timeLimit=:e, memoryLimit=:f, fullFeedback=:g, analysisVisible=:h, customChecker=:i,attachments=:j,superhidden=:l,createdTime=:m, editorials=:n, editorialVisible=:o, EE=:p, contestUsers=:q',
        ExpressionAttributeValues={':a':info['title'], ':b':info['source'], ':c':info['author'], ':d':info['problem_type'], ':e':info['timeLimit'], ':f':info['memoryLimit'], ':g':info['fullFeedback'], ':h':info['analysisVisible'], ':i':info['customChecker'], ':j':info['attachments'], ':l':info['superhidden'], ':m':info['createdTime'], ':n':info['editorials'], ':o':info['editorialVisible'],':p':info['EE'],':q':info['contestUsers']},
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
    res = lambda_client.invoke(FunctionName = 'arn:aws:lambda:ap-southeast-1:354145626860:function:codebreaker-problem-verification', InvocationType='RequestResponse', Payload = json.dumps(lambda_input))

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
    info['createdTime'] = (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %X")
    info['editorials'] = []
    info['editorialVisible'] = False
    updateProblemInfo(problem_id, info)
    subtasks = {}
    subtasks['subtaskScores'] = []
    subtasks['subtaskDependency'] = []
    subtasks['subtaskScores'].append(100)
    subtasks['subtaskDependency'].append('1')
    updateSubtaskInfo(problem_id, subtasks)
    extras = {}
    extras['noACs'] = 0
    extras['testcaseCount'] = 0
    problems_table.update_item(
        Key = {'problemName' : problem_id},
        UpdateExpression = f'set noACs=:a, testcaseCount=:b',
        ExpressionAttributeValues={':a':extras['noACs'], ':b':extras['testcaseCount']}
    )
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

    res = lambda_client.invoke(FunctionName = 'arn:aws:lambda:ap-southeast-1:354145626860:function:codebreaker-regrade-problem', InvocationType='Event', Payload = json.dumps(lambda_input))    
