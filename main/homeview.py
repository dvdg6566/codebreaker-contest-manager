from flask import flash, render_template, session, request, redirect
from datetime import datetime
import awstools

def home():
	userinfo = awstools.users.getCurrentUserInfo()

	if not userinfo or userinfo['contest'] == None:
		return render_template("home.html", userinfo=userinfo, contestinfo=None)

	contestinfo = awstools.contests.getContestInfo(contestId = userinfo['contest'])
	
	startTime = datetime.strptime(contestinfo['startTime'], "%Y-%m-%d %X")
	endTime = datetime.strptime(contestinfo['endTime'], "%Y-%m-%d %X")
	curTime = datetime.utcnow()
	if curTime > endTime:
		contestinfo['status'] = 'ENDED'
	elif curTime <= endTime and curTime >= startTime:
		contestinfo['status'] = 'ONGOING'
	else:
		contestinfo['status'] = 'NOT_STARTED'

	problemNames = contestinfo['problems']
	problems = []
	for problem in problemNames: 
		problemInfo = awstools.problems.getProblemInfo(problem)
		problems.append(problemInfo)

	print(userinfo)
	print(problems)
	for problem in problems:
		if problem['problemName'] in userinfo['problemScores']: 
			problem['score'] = userinfo['problemScores'][problem['problemName']]
		else:
			problem['score'] = 'N/A'

	return render_template("home.html", userinfo=userinfo, contestinfo=contestinfo, problems=problems)