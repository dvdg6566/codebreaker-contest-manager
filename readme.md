# Codebreaker Contest Manager

Codebreaker Contest Manager is a fully automated deployment of the Codebreaker Online Judge architecture for the planning and running of contests.  

Key Features:
- Based on Infrastructure As a Code (IAAC) and Continuous Deployment (CD) technologies, which allow automated deployment into independent AWS accounts to maintain least-privillege of testdata and resources.
   - Deployment does not require execution of any scripts, SSH or AWS configuration. 
- Completely serverless compilation, grading and databases to allow for infinite scalability
- Back-end that automatically syncs with Codebreaker Online Judge allowing for easy transfer of problems onto analysis mode.

Technical Stack: 
- Compilation executed serverlessly on ubuntu 20.04 (based on ioi 2021 rules) with 1592MB memory running on AWS Lambda and Elastic Container Registry
- Grading executed serverlessly on Amazon Linux 2.0  with 1600 or 2600 MB of memory running on AWS Lambda orchestrated by Express AWS Step Functions
- Front-end Flask server running on a t2.micro AWS EC2 instance
- Authentication performed using AWS Cognito
- Main data storage on AWS S3, databases on AWS DynamoDB. Testcases are uploaded with temporary client-side tokens generated with AWS Security Token Service (STS) through Identity and Access Management (IAM)
- Announcements and Clarification notifications implemented through AWS API Gateway WebSockets
- Automated deployment using AWS Serverless Application Model (SAM) and AWS CloudFormation 
