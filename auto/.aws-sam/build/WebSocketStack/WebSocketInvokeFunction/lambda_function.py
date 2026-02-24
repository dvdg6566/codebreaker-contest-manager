import json
import awstools

def lambda_handler(event, context):
    
    notificationType = event['notificationType']
    # Notification type is either announce (all users) or clarification (admin only)
    connectionIds = event['connectionIds']

    body = {'notificationType': notificationType}

    for connectionId in connectionIds:
        awstools.invoke(connectionId, body)

    return {'status':200}

'''
Structure of event:
{
    'notificationType': 'announce',
    'connectionIds': [
        'A','B'
    ]
}
'''