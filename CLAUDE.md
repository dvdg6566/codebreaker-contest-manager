# Codebreaker Contest Manager

## Project Overview

A serverless contest management system using AWS SAM, Lambda, DynamoDB, S3, Step Functions, and API Gateway WebSockets.

## Architecture

### Nested Stack Structure

The SAM template is split into nested stacks for maintainability:

```
auto/
├── template.yml              # Main orchestrator
└── templates/
    ├── storage.yml           # S3 buckets
    ├── database.yml          # DynamoDB tables
    ├── cognito.yml           # User authentication
    ├── codebuild.yml         # ECR + CodeBuild + Compiler Lambda (auto-deployed)
    ├── lambdas.yml           # Lambda functions
    ├── websocket.yml         # WebSocket API Gateway
    └── step-functions.yml    # State machines
```

### Compiler Lambda Auto-Deployment (Implemented)

The compiler Lambda is automatically deployed via a CloudFormation Custom Resource:

1. **CodeBuildTriggerFunction** - Lambda that handles Custom Resource lifecycle
2. **CodeBuildTrigger** - Custom Resource that triggers on stack create/update
3. On Create/Update:
   - Triggers CodeBuild project
   - Waits for Docker image build (~5-10 min)
   - Creates/updates the Compiler Lambda from ECR image
4. On Delete:
   - Deletes the Compiler Lambda

**Files:**
- `auto/lambda-functions/codebuild-trigger/lambda_function.py` - Custom Resource handler
- `auto/templates/codebuild.yml` - Contains CodeBuildTriggerFunction, CodeBuildTrigger, and related resources

## Deployment

```bash
cd auto
sam build && sam deploy --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

Initial deployment takes ~10-15 minutes due to CodeBuild.

See `auto/instructions.md` for detailed deployment instructions.
