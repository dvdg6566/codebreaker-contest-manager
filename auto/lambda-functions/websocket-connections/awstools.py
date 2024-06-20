import os
import boto3
from time import time
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
judgeName = os.environ['judgeName']
webSocketTable = dynamodb.Table(f'{judgeName}-websocket')

def addConnection(connectionId, accountRole='member', username='placeholder'):
    # Timedelta 5h = 2 hours * 60 miinutes per hour * 6 seconds per minute 
    expiryTime = int(time()) + 5 * 60 * 60 
    
    connection = {
        'connectionId': connectionId,
        'accountRole': accountRole,
        'username': username,
        'expiryTime': expiryTime
    }
    
    webSocketTable.put_item(Item = connection)
    
def removeConnection(connectionId):
    try:
        resp = webSocketTable.delete_item(
            Key = {'connectionId': connectionId}
        )
    except Exception as e:
        print(e)

def updateUserDetails(connectionId, username, accountRole):
    webSocketTable.update_item(
        Key = {'connectionId': connectionId},
        UpdateExpression = f'set username=:u, accountRole=:r',
        ExpressionAttributeValues = {':u': username, ':r': accountRole}
    )