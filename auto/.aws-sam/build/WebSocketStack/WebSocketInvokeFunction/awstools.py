import os
import json
import boto3

webSocketURI = os.environ['WebSocketURI']
apigateway = boto3.client('apigatewaymanagementapi', endpoint_url=webSocketURI)

def invoke(connectionId, body):
    try:
        apigateway.post_to_connection(
            ConnectionId = connectionId,
            Data = json.dumps(body)
        )
    except: 
    # If posting fails for whatever reason, just ignore
        pass