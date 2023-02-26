from flask import render_template, redirect, flash, request, session, make_response
from forms import ResubmitForm

import os
import awstools
from time import sleep 
from datetime import datetime, timedelta

TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET'))
#BEGIN: SUBMISSION -----------------------------------------------------------------------------------------------------------------------------------------------------

def submission(subId):
	userInfo = awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect(url_for("login", next=request.url))

	# ACCESS CONTROL
	if userInfo['role'] == 'member': 
		contestInfo = awstools.contests.getContestInfo(userInfo['contest'])
		if contestInfo == None or contestInfo['status'] != 'ONGOING':
			flash("This resource is only accessible during contests!", "warning")
			return redirect('/')

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

	problemName = subDetails['problemName']
	username = subDetails['username']
	problemInfo = awstools.problems.getProblemInfo(problemName)

	# Convert into specific imezone
	def convertToLocalTimezone(timestring, offset):
		if timestring == '': return ''
		timestamp = datetime.strptime(timestring, "%Y-%m-%d %X")
		timestamp += timedelta(hours=offset)
		newTimestring = timestamp.strftime("%Y-%m-%d %X")
		newTimestring += f' (GMT+{offset})' if offset >= 0 else f' (GMT{offset})'
		return newTimestring
	subDetails['submissionTime'] = convertToLocalTimezone(subDetails['submissionTime'], TIMEZONE_OFFSET)
	subDetails['gradingCompleteTime'] = convertToLocalTimezone(subDetails['gradingCompleteTime'], TIMEZONE_OFFSET)

	# Set time and memory to NA for compile errors 
	if 'compileErrorMessage' in subDetails.keys():
		subDetails['maxTime'] = 'N/A'
		subDetails['maxMemory'] = 'N/A'
	else:
		subDetails['compileErrorMessage'] = ''
		subDetails['maxTime'] = f'{subDetails["maxTime"]} seconds'
		subDetails['maxMemory'] = f'{subDetails["maxMemory"]} MB'

	if problemInfo['problem_type'] == 'Communication' and 'code' in subDetails:
		flash('This submission was made before the problem type was converted to communication', 'warning')

	subtaskMaxScores = problemInfo['subtaskScores']
	subtaskNumber = len(subtaskMaxScores)
	subtaskDependency = problemInfo['subtaskDependency']
	testcaseNumber = problemInfo['testcaseCount']
	fullFeedback = problemInfo['fullFeedback']

	totalScore = 0
	verdicts = subDetails['verdicts']
	times = [round(x,2) for x in subDetails['times']]
	scores = [formatFloat(i) for i in subDetails['score']]
	memories = [round(x) for x in subDetails['memories']]
	subtaskScores = [formatFloat(i) for i in subDetails['subtaskScores']]
	subtaskDetails = []
	
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
					continue
				elif not fullFeedback and nonAC:
					detail['testcases'].append({'score' : '-', 'verdict' :'N/A', 'time': 'N/A', 'memory': 'N/A'})
				else:
					if scores[ind] == 0:
						nonAC = True # Still continue to show feedback for partial scoring
					detail['testcases'].append({'score' : scores[ind], 'verdict' : verdicts[ind], 'time': times[ind], 'memory': memories[ind]})
				if verdicts[ind] == ":(":
					detail['done'] = False
				if scores[ind] == 0 and verdicts[ind] != "AC" and verdicts[ind] != "PS":
					detail['verdict'] = 'WA'
					stopVerdict = 1
				if scores[ind] != 100 and verdicts[ind] == "PS" and detail['verdict'] != 'WA':
					detail['verdict'] = 'PS'
				minScore = min(minScore, scores[ind])
		detail['yourScore'] = max(detail['yourScore'], maxScore * minScore / 100)
		detail['yourScore'] = formatFloat(detail['yourScore'])
		totalScore += detail['yourScore']

		subtaskDetails.append(detail)
	
	if len(scores) < testcaseNumber:
		flash("If you see the 'UG' verdict, it means that testcases were added after this submission was graded", "warning")
	if len(subtaskMaxScores) != len(subtaskScores):
		flash("Some subtasks were added or removed from this question after this submission was graded", "warning")

	'''RESUBMISSION'''
	form = ResubmitForm()

	if form.is_submitted():
		subDetails = awstools.submissions.getSubmission(int(subId))
		result = request.form
		if 'form_name' in result and result['form_name'] == 'regrade':
			''' REGRADE: ONLY ADMIN CAN REGRADE'''
			if userInfo != None and userInfo['role'] != 'admin':
				flash('You do not have permission to regrade!','warning')
				return redirect(f'/problem/{problemName}')

			# For regrade, the code is already there so we just call grade 
			awstools.grading.startGrading(
				problemName = problemName,
				submissionId = subId,
				username = subDetails['username'], 
				submissionTime = subDetails['submissionTime'],
				language = subDetails['language'],
				problemType = problemInfo['problem_type']
			)

			sleep(2)
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
			language = subDetails['language']
		)

		if response['status'] != 200:
			flash(response['error'], "warning")
			return redirect(f'/problem/{problemName}')

		sleep(2)
		return redirect(f"/submission/{response['subId']}")

	'''END RESUBMISSION'''

	return render_template('submission.html',subDetails=subDetails,probleminfo=problemInfo, userinfo=userInfo,form=form,subtaskDetails=subtaskDetails)

#END: SUBMISSION -----------------------------------------------------------------------------------------------------------------------------------------------------
