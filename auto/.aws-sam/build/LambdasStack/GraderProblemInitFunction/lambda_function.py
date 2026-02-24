import awstools
from datetime import datetime

def lambda_handler(event, context):
    
    problemName = event['problemName']
    submissionId = event['submissionId']
    username = event['username']
    subTime = event['submissionTime']
    language = event['language'] # Language should be from "py" or "cpp"
    
    problemInfo = awstools.getProblemInfo(problemName)

    timeLimit = problemInfo['timeLimit']
    memoryLimit = problemInfo['memoryLimit']
    if memoryLimit=="":memoryLimit=1024
    if timeLimit=="":timeLimit=1
    subtaskDependency = problemInfo['subtaskDependency']
    subtaskMaxScores = problemInfo['subtaskScores']
    subtaskNumber = len(subtaskDependency)
    testcaseNumber = int(problemInfo['testcaseCount'])
    customChecker = problemInfo['customChecker']
    
    times = [0 for i in range(testcaseNumber+1)]
    memories = [0 for i in range(testcaseNumber+1)]
    scores = [0 for i in range(testcaseNumber+1)]
    verdicts = [":(" for i in range(testcaseNumber+1)]
    subtaskScores = [0 for i in range(subtaskNumber)]
    returnCodes = [0 for i in range(testcaseNumber+1)]
    status = [1 for i in range(testcaseNumber+1)]
    
    submission_upload = {
        "subId": submissionId,
        "submissionTime": subTime,
        "gradingTime": (datetime.utcnow()).strftime("%Y-%m-%d %X"),
        "gradingCompleteTime": '',
        "username": username,
        "maxMemory":0,
        "maxTime":0,
        "problemName":problemName,
        "score":scores,
        "verdicts":verdicts,
        "times":times,
        "memories":memories,
        "returnCodes":returnCodes,
        "subtaskScores":subtaskScores,
        "status":status,
        "totalScore":0,
        "language": language
    }
    
    awstools.uploadSubmission(submission_upload)
    
    # GENERATES LAMBDA INPUT TO SEND TO STATE MACHINE

    output = {
        'status': 200,
        'payloads': [],
        'username': username,
    }
    
    for i in range(1, testcaseNumber + 1):
        output['payloads'].append({
            'problemName': problemName,
            'submissionId': submissionId, 
            'testcaseNumber': i,
            'memoryLimit': float(memoryLimit),
            'timeLimit': float(timeLimit),
            'customChecker': int(customChecker),
            'language': language
        })
    
    return output
    
