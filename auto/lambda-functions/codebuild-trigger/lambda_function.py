"""
CloudFormation Custom Resource Lambda for triggering CodeBuild and creating the Compiler Lambda.

This Lambda:
1. On Create/Update: Triggers CodeBuild, waits for completion, creates/updates the Compiler Lambda
2. On Delete: Deletes the Compiler Lambda function
"""

import boto3
import time
import json
import urllib.request

codebuild = boto3.client('codebuild')
lambda_client = boto3.client('lambda')
sts = boto3.client('sts')


def send_response(event, context, status, data=None, reason=None):
    """Send response to CloudFormation pre-signed URL."""
    response_body = {
        'Status': status,
        'Reason': reason or f'See CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId': event.get('PhysicalResourceId', context.log_stream_name),
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': data or {}
    }

    response_body_json = json.dumps(response_body).encode('utf-8')

    req = urllib.request.Request(
        event['ResponseURL'],
        data=response_body_json,
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )

    urllib.request.urlopen(req)


def wait_for_build(build_id, max_attempts=120):
    """Poll CodeBuild until build completes. Max ~20 minutes."""
    for _ in range(max_attempts):
        time.sleep(10)

        response = codebuild.batch_get_builds(ids=[build_id])
        build = response['builds'][0]
        status = build['buildStatus']

        print(f'Build status: {status}')

        if status == 'SUCCEEDED':
            return True, status
        elif status in ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT']:
            return False, status

    return False, 'TIMEOUT'


def create_compiler_lambda(judge_name, image_uri, role_arn):
    """Create or update the Compiler Lambda function."""
    function_name = f'{judge_name}-compiler'
    account_id = sts.get_caller_identity()['Account']

    try:
        # Try to update existing function
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ImageUri=image_uri
        )
        print(f'Updated existing Lambda function: {function_name}')
        return response['FunctionArn']
    except lambda_client.exceptions.ResourceNotFoundException:
        # Create new function
        response = lambda_client.create_function(
            FunctionName=function_name,
            PackageType='Image',
            Code={'ImageUri': image_uri},
            Role=role_arn,
            Timeout=60,
            MemorySize=1600,
            Environment={
                'Variables': {
                    'AWS_ACCOUNT_ID': account_id,
                    'judgeName': judge_name
                }
            }
        )
        print(f'Created new Lambda function: {function_name}')
        return response['FunctionArn']


def delete_compiler_lambda(judge_name):
    """Delete the Compiler Lambda function."""
    function_name = f'{judge_name}-compiler'

    try:
        lambda_client.delete_function(FunctionName=function_name)
        print(f'Deleted Lambda function: {function_name}')
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f'Lambda function {function_name} does not exist, skipping delete')


def lambda_handler(event, context):
    print(f'Received event: {json.dumps(event)}')

    request_type = event['RequestType']
    properties = event['ResourceProperties']

    project_name = properties['ProjectName']
    judge_name = properties['JudgeName']
    image_uri = properties['ImageUri']
    compiler_role_arn = properties['CompilerRoleArn']

    try:
        if request_type == 'Delete':
            delete_compiler_lambda(judge_name)
            send_response(event, context, 'SUCCESS')
            return

        # Create or Update
        print(f'Starting CodeBuild project: {project_name}')
        build_response = codebuild.start_build(projectName=project_name)
        build_id = build_response['build']['id']
        print(f'Build started: {build_id}')

        # Wait for build to complete
        success, status = wait_for_build(build_id)

        if not success:
            send_response(event, context, 'FAILED',
                         reason=f'CodeBuild failed with status: {status}')
            return

        # Create/update the Compiler Lambda
        function_arn = create_compiler_lambda(judge_name, image_uri, compiler_role_arn)

        send_response(event, context, 'SUCCESS', {
            'BuildId': build_id,
            'CompilerFunctionArn': function_arn
        })

    except Exception as e:
        print(f'Error: {str(e)}')
        send_response(event, context, 'FAILED', reason=str(e))
