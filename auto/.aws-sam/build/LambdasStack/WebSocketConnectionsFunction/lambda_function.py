import json
import awstools

def lambda_handler(event, context):
    
    route = event['requestContext']['routeKey']
    connectionId = event['requestContext']['connectionId']
    print(route)
    
    if route == '$connect':
        # Connect: Add connection entry to dynamo DB
        # Connection will also have a TTL for 2 hours later
        awstools.addConnection(connectionId = connectionId)
    elif route == '$disconnect':
        # Disconnect: Remove connection entry from dynamo DB
        awstools.removeConnection(connectionId = connectionId)
    else:
        # Supplying username and account role
        body = json.loads(event['body'])
        username = body['username']
        accountRole = body['accountRole']
        awstools.updateUserDetails(connectionId = connectionId, username = username, accountRole = accountRole)
        # print(f'Subscribing for {username} with role {accountRole}')
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
