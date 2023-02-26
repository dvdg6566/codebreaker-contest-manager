from flask import flash, render_template, session, request, redirect

from datetime import datetime
import awstools

def home():
	userinfo = awstools.users.getCurrentUserInfo()

	if not userinfo or userinfo['contest'] == None:
		return render_template("home.html", userinfo=userinfo, contestinfo=None)

	contestinfo = awstools.contests.getContestInfo(contestId = userinfo['contest'])
	if contestinfo == None: # No registered contest
		return render_template("home.html", userinfo=userinfo, contestinfo=None)

	problemNames = contestinfo['problems']
	problems = []
	for problem in problemNames: 
		problemInfo = awstools.problems.getProblemInfo(problem)
		problems.append(problemInfo)

	for problem in problems:
		if problem['problemName'] in userinfo['problemScores']: 
			problem['score'] = userinfo['problemScores'][problem['problemName']]
		else:
			problem['score'] = 0

	score = {}
	score['user'] = sum([problem['score'] for problem in problems if problem['score'] != 'N/A'])
	score['total'] = 100 * len(problems)

	return render_template("home.html", userinfo=userinfo, contestinfo=contestinfo, problems=problems, score=score)