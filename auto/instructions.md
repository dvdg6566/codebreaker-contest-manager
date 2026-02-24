# Codebreaker Contest Manager - Deployment Instructions

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Docker installed (for local testing)
- An S3 bucket for storing deployment artifacts

## Project Structure

```
auto/
├── template.yml              # Main orchestrator
├── templates/
│   ├── storage.yml           # S3 buckets
│   ├── database.yml          # DynamoDB tables
│   ├── cognito.yml           # User authentication
│   ├── codebuild.yml         # ECR + CodeBuild for compiler
│   ├── lambdas.yml           # Lambda functions
│   ├── websocket.yml         # WebSocket API Gateway
│   └── step-functions.yml    # State machines
├── lambda-functions/         # Lambda source code
├── state-machines/           # Step Function definitions
└── samconfig.toml            # SAM deployment configuration
```

---

## Local Development

### Validate Templates

```bash
# Validate main template
sam validate --template template.yml

# Validate individual nested templates
sam validate --template templates/storage.yml
sam validate --template templates/database.yml
sam validate --template templates/cognito.yml
sam validate --template templates/codebuild.yml
sam validate --template templates/lambdas.yml
sam validate --template templates/websocket.yml
sam validate --template templates/step-functions.yml
```

### Build

```bash
sam build --template template.yml
```

---

## Deployment

### Option 1: Interactive Deployment (Development)

```bash
sam deploy --guided --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

This will prompt for:
- Stack name
- AWS region
- JudgeName parameter
- S3 bucket for artifacts
- Confirmation of IAM resource creation

### Option 2: Non-Interactive Deployment

```bash
sam build --template template.yml

sam deploy \
  --stack-name codebreaker-contest \
  --parameter-overrides JudgeName=mycontest \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --resolve-s3
```

### Option 3: Using samconfig.toml

After running `sam deploy --guided` once, settings are saved to `samconfig.toml`. Subsequent deployments:

```bash
sam build && sam deploy
```

---

## Packaging for One-Click Deployment

To create a CloudFormation Quick Create link, you need to package and host the templates in S3.

### Step 1: Create an S3 Bucket for Templates

```bash
aws s3 mb s3://codebreaker-templates-<your-unique-suffix> --region <your-region>
```

### Step 2: Package the Templates

```bash
sam package \
  --template-file template.yml \
  --output-template-file packaged.yml \
  --s3-bucket codebreaker-templates-<your-unique-suffix> \
  --s3-prefix templates
```

This uploads:
- Lambda code zip files to S3
- Nested templates to S3
- Produces `packaged.yml` with S3 URLs

### Step 3: Upload the Packaged Main Template

```bash
aws s3 cp packaged.yml s3://codebreaker-templates-<your-unique-suffix>/packaged.yml
```

### Step 4: Make Templates Public (for public Quick Create link)

```bash
# Option A: Make bucket public (use with caution)
aws s3api put-bucket-policy --bucket codebreaker-templates-<your-unique-suffix> --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicRead",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::codebreaker-templates-<your-unique-suffix>/*"
  }]
}'

# Option B: Make specific objects public
aws s3api put-object-acl --bucket codebreaker-templates-<your-unique-suffix> --key packaged.yml --acl public-read
```

### Step 5: Generate Quick Create Link

```
https://console.aws.amazon.com/cloudformation/home#/stacks/quickcreate
  ?templateURL=https://codebreaker-templates-<your-unique-suffix>.s3.amazonaws.com/packaged.yml
  &stackName=codebreaker
  &param_JudgeName=mycontest
```

URL-encoded version:
```
https://console.aws.amazon.com/cloudformation/home#/stacks/quickcreate?templateURL=https%3A%2F%2Fcodebreaker-templates-<your-unique-suffix>.s3.amazonaws.com%2Fpackaged.yml&stackName=codebreaker&param_JudgeName=mycontest
```

---

## Post-Deployment Steps

### 1. Build Compiler Image (Manual - until Custom Resource is implemented)

After the stack is deployed, run the compiler initialization script:

```bash
cd ../init
python compiler.py
```

This:
- Triggers the CodeBuild project
- Waits for the Docker image to be built
- Creates the compiler Lambda function from the ECR image

### 2. Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name codebreaker-contest

# List stack outputs
aws cloudformation describe-stacks --stack-name codebreaker-contest --query 'Stacks[0].Outputs'
```

### 3. Test Lambda Functions

```bash
# Test problem validation
aws lambda invoke \
  --function-name mycontest-problem-validation \
  --payload '{"problemName": "addition"}' \
  response.json

cat response.json
```

---

## Updating the Stack

```bash
# Make changes to templates, then:
sam build && sam deploy
```

For one-click deployment updates:
```bash
sam package \
  --template-file template.yml \
  --output-template-file packaged.yml \
  --s3-bucket codebreaker-templates-<your-unique-suffix> \
  --s3-prefix templates

aws s3 cp packaged.yml s3://codebreaker-templates-<your-unique-suffix>/packaged.yml
```

---
