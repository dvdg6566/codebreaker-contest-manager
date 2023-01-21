import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

judgeName = 'codebreakercontest'
clarifications_table = dynamodb.Table(f'{judgeName}-clarifications')

def createClarification(username, question, problemId):
    clarificationId = getNextClarificationId()
    info = {}
    info['askedBy'] = username
    info['question'] = question
    info['problemId'] = problemId
    info['answer'] = ""
    info['answeredBy'] = ""
    updateClarificationInfo(clarificationId, info)

def updateClarificationInfo(clarificationId, info):
    clarifications_table.update_item(
        Key = {'clarificationId':clarificationId},
        UpdateExpression = f'set askedBy=:a,question=:b,problemId=:c,answer=:d,answeredBy=:e',
        ExpressionAttributeValues={':a':info['askedBy'],':b':info['question'],':c':info['problemId'],':d':info['answer'],':e':info['answeredBy']}
    )

def getClarificationInfo(clarificationId):
    response = clarifications_table.query(
        KeyConditionExpression = Key('clarificationId').eq(clarificationId)
    )
    clarification_info = response['Items']
    if len(clarification_info) == 0:
        return None
    return clarification_info[0]

def getClarificationsByUser(username):
    response = clarifications_table.query(
        IndexName = 'askedByIndex',
        KeyConditionExpression = Key('askedBy').eq(username),
    )
    return response['Items']

def getAllClarifications():
    return scan(clarifications_table)