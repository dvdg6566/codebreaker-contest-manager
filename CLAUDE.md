# Codebreaker Contest Manager

## Project Overview

A serverless contest management system using AWS SAM, Lambda, DynamoDB, S3, Step Functions, and API Gateway WebSockets.

## Implementation Plan: One-Click Deployment for Compiler Lambda

### Problem

Currently, deploying the compiler Lambda requires a manual bootstrap step (`init/compiler.py`) because:
- CloudFormation creates the ECR repository and CodeBuild project
- But the Docker image must exist before the Lambda can be created
- Lambda only supports private ECR (not ECR Public), so we can't use a pre-built public image

### Solution: CodeBuild + Custom Resource

Automate the build trigger within CloudFormation using a Custom Resource.

### Implementation Steps

#### 1. Create CodeBuild Trigger Lambda

Create `auto/lambda-functions/codebuild-trigger/lambda_function.py`:

```python
import boto3
import cfnresponse
import time

codebuild = boto3.client('codebuild')

def lambda_handler(event, context):
    try:
        if event['RequestType'] == 'Delete':
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            return

        project_name = event['ResourceProperties']['ProjectName']

        # Start build
        response = codebuild.start_build(projectName=project_name)
        build_id = response['build']['id']

        # Poll for completion (max ~10 min)
        for _ in range(60):
            time.sleep(10)
            builds = codebuild.batch_get_builds(ids=[build_id])
            status = builds['builds'][0]['buildStatus']

            if status == 'SUCCEEDED':
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {'BuildId': build_id})
                return
            elif status in ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT']:
                cfnresponse.send(event, context, cfnresponse.FAILED, {'Error': f'Build {status}'})
                return

        cfnresponse.send(event, context, cfnresponse.FAILED, {'Error': 'Build timeout'})
    except Exception as e:
        cfnresponse.send(event, context, cfnresponse.FAILED, {'Error': str(e)})
```

#### 2. Update template.yml

Add the trigger Lambda and Custom Resource:

```yaml
CodeBuildTriggerFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: !Sub ${JudgeName}-codebuild-trigger
    CodeUri: lambda-functions/codebuild-trigger
    Timeout: 900  # 15 min max for Custom Resource
    Policies:
      - Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Action:
              - codebuild:StartBuild
              - codebuild:BatchGetBuilds
            Resource: !GetAtt CodeBuildProject.Arn

CodeBuildTrigger:
  Type: Custom::CodeBuildTrigger
  DependsOn: CodeBuildProject
  Properties:
    ServiceToken: !GetAtt CodeBuildTriggerFunction.Arn
    ProjectName: !Ref CodeBuildProject

CompilerFunction:
  Type: AWS::Lambda::Function
  DependsOn: CodeBuildTrigger
  Properties:
    FunctionName: !Sub ${JudgeName}-compiler
    PackageType: Image
    Code:
      ImageUri: !Sub ${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/${JudgeName}-compiler-repository:latest
    Role: !GetAtt CompilerFunctionIAMRole.Arn
    Timeout: 60
    MemorySize: 1600
    Environment:
      Variables:
        judgeName: !Ref JudgeName
        AWS_ACCOUNT_ID: !Ref AWS::AccountId
```

#### 3. Clean Up

After implementation, delete:
- `init/compiler.py` (no longer needed)

### Benefits

- True one-click deployment via CloudFormation Quick Create link
- No manual bootstrap steps
- Self-contained stack creation
- Users build their own image (no trust issues with pre-built images)

### Trade-offs

- Initial deployment takes ~10 minutes (CodeBuild time)
- CodeBuild costs apply to users (~$0.005 per build minute)
