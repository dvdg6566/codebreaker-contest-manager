from flask import render_template, redirect, flash, request, session, make_response
import datetime
import time
import random

import awstools
from forms import ResubmitForm

#BEGIN: SUBMISSION -----------------------------------------------------------------------------------------------------------------------------------------------------

def submission(subId):
	userInfo = awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect(url_for("login", next=request.url))

	# if not awstools.users.judgeAccess(userInfo):
	# return redirect('/')

	if not subId.isdigit():
		flash("Sorry, the submission you're looking for doesn't exist", "warning")
		return redirect('/')

	subDetails = awstools.submissions.getSubmission(int(subId))
	if subDetails == None:
		flash ("Sorry, the submission you're looking for doesn't exist.", "warning")
		return redirect('/')

	if userInfo['role'] != 'admin' and userInfo['username'] != subDetails['username']:
		flash ("You do not have access to this resource!", "warning")
		return redirect('/')

	# Format and round floats
	def formatFloat(x):
		x = round(x,2)
		if x == round(x): return round(x)
		return x

	subtaskScores = [formatFloat(i) for i in subDetails['subtaskScores']]
	scores = [formatFloat(i) for i in subDetails["score"]]
	language = subDetails['language']

	problemName = subDetails['problemName']
	username = subDetails['username']
	problemInfo = awstools.problems.getProblemInfo(problemName)
	if type(problemInfo) == str:
		return "Sorry, this problem doesn't exist"
	totalScore = 0
	verdicts = subDetails['verdicts']
	times = [round(x,2) for x in subDetails['times']]
	memories = [round(x) for x in subDetails['memories']]
	maxTime = round( max(max(subDetails['times']), float(subDetails['maxTime'])), 3);
	maxMemory = round( max(max(subDetails['memories']), float(subDetails['maxMemory'])), 2);
	submissionTime = subDetails['submissionTime']
	gradingTime = subDetails['gradingTime']
	
	code = None
	codeA = None
	codeB = None

	if 'code' in subDetails.keys():
		code= subDetails['code']
	else:
		# Communication problem
		codeA = subDetails['codeA']
		codeB = subDetails['codeB']

	if 'compileErrorMessage' in subDetails.keys():
		subDetails['maxTime'] = 'N/A'
		subDetails['maxMemory'] = 'N/A'
	else:
		subDetails['compileErrorMessage'] = ''
		subDetails['maxTime'] = f'{subDetails["maxTime"]} seconds'
		subDetails['maxMemory'] = f'{subDetails["maxMemory"]} MB'

	if problemInfo['problem_type'] == 'Communication' and code != None:
		flash('This submission was made before the problem type was converted to communication', 'warning')

	subtaskMaxScores = problemInfo['subtaskScores']
	subtaskNumber = len(subtaskMaxScores)
	subtaskDependency = problemInfo['subtaskDependency']
	testcaseNumber = problemInfo['testcaseCount']
	fullFeedback = problemInfo['fullFeedback']

	toRefresh = False
	subtaskDetails = []

	changed = False
	changedSubtask = (len(subtaskMaxScores) != len(subtaskScores))
	
	for i in range(subtaskNumber):
		maxScore = subtaskMaxScores[i]
		yourScore = 0
		if i < len(subtaskScores):
			yourScore = subtaskScores[i]

		yourScore = formatFloat(maxScore*yourScore/100)
		detail = {'number' : i, 'maxScore': maxScore, 'yourScore': yourScore, 'verdict': 'AC', 'testcases' : [], 'done' : True}
		stopVerdict = 0
		
		minScore = 100 #recalculate here cause of updating issues
		dep = subtaskDependency[i].split(',')
		nonAC = False
		for t in dep:
			x = t.split('-')
			
			TC = []
			if(len(x) == 1):
				ind = int(x[0])
				TC.append(ind)
			else:
				st = int(x[0])
				en = int(x[1])
				for j in range(st,en+1):
					TC.append(j)
			for ind in TC:
				if len(scores) <= ind:
					detail['testcases'].append({'score' : '-', 'verdict' :'UG', 'time': 'N/A', 'memory': 'N/A'})
					changed = True
					continue
				elif not fullFeedback and nonAC:
					detail['testcases'].append({'score' : '-', 'verdict' :'N/A', 'time': 'N/A', 'memory': 'N/A'})
				else:
					if scores[ind] == 0:
						nonAC = True # Still continue to show feedback for partial scoring
					detail['testcases'].append({'score' : scores[ind], 'verdict' : verdicts[ind], 'time': times[ind], 'memory': memories[ind]})
				if verdicts[ind] == ":(":
					detail['done'] = False
					toRefresh = True
				if scores[ind] == 0 and verdicts[ind] != "AC" and verdicts[ind] != "PS":
					detail['verdict'] = 'WA'
					stopVerdict = 1
				if scores[ind] != 100 and verdicts[ind] == "PS" and detail['verdict'] != 'WA':
					detail['verdict'] = 'PS'
				minScore = min(minScore, scores[ind])
		detail['yourScore'] = max(detail['yourScore'], maxScore * minScore / 100)
		detail['yourScore'] = formatFloat(detail['yourScore'])
		totalScore += detail['yourScore']

		diffInTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=8) - datetime.datetime.strptime(gradingTime, '%Y-%m-%d %H:%M:%S')).total_seconds()

		subtaskDetails.append(detail)
	
	# If submission was submitted more than 1 minute ago, or if submission is compile error, don't refresh
	if diffInTime > 60 or subDetails['compileErrorMessage'] != '':
		toRefresh = False
	if changed:
		flash("If you see the 'UG' verdict, it means that testcases were added after this submission was graded", "warning")
	if changedSubtask:
		flash("Some subtasks were added or removed from this question after this submission was graded", "warning")

	'''RESUBMISSION'''
	form = ResubmitForm()

	if form.is_submitted():
		result = request.form
		if 'form_name' in result and result['form_name'] == 'regrade':
			''' REGRADE: ONLY ADMIN CAN REGRADE'''
			if userInfo != None and userInfo['role'] != 'admin':
				flash('You do not have permission to regrade!','warning')
				return redirect(f'/problem/{problemName}')

			# For regrade, the code is already there so we just call grade 
			awstools.submissions.startGrading(
				problemName = problemName,
				submissionId = subId,
				username = subDetails['username'], 
				submissionTime = subDetails['submissionTime'],
				language = language,
				problemType = problemInfo['problem_type']
			)

			time.sleep(2)
			return redirect(f"/submission/{subId}")
		
		''' RESUBMIT '''
		if userInfo == None:
			flash('You do not have permission to submit!','warning')
			return redirect(f'/problem/{problemName}')
		
		if not problemInfo['validated']:
			flash("Sorry, this problem is still incomplete.", "warning")
			return redirect(f'/problem/{problemName}')

		''' GRADING '''
		response = awstools.grading.gradeSubmission(
			form = request.form,
			problemInfo = problemInfo,
			userInfo = userInfo,
			language = language
		)

		if response['status'] != 200:
			flash(response['error'], "warning")
			return redirect(f'/problem/{problemName}')

		time.sleep(2)
		return redirect(f"/submission/{response['subId']}")

	'''END RESUBMISSION'''

	return render_template('submission.html', message="",subDetails=subDetails,probleminfo=problemInfo, userinfo=userInfo,toRefresh=toRefresh,form=form,code=code,codeA=codeA,codeB=codeB,subtaskDetails=subtaskDetails)

#END: SUBMISSION -----------------------------------------------------------------------------------------------------------------------------------------------------
