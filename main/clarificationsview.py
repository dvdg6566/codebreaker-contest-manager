from flask import flash, render_template, session, request, redirect, url_for
from forms import askClarificationForm, answerClarificationForm

import os
import awstools
from datetime import datetime, timedelta

# Gets timezone from environment variables
TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET'))

def clarifications():
	userInfo=awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect(url_for("login", next=request.url))
	username = userInfo['username']

	# ACCESS CONTROL
	if userInfo['role'] == 'member': 
		contestInfo = awstools.contests.getContestInfo(userInfo['contest'])
		if contestInfo == None or contestInfo['status'] != 'ONGOING':
			flash("This resource is only accessible during contests!", "warning")
			return redirect('/')

	# Get list of clarifications to display
	if userInfo['role'] == 'admin':
		clarifications = awstools.clarifications.getAllClarifications()
		clarifications.sort(key=lambda x:x['clarificationTime'], reverse=True)
	else:
		clarifications = awstools.clarifications.getClarificationsByUser(username=username)
		
	# Convert timezone of clarifications
	for clarification in clarifications:
		timestamp = datetime.strptime(clarification['clarificationTime'], "%Y-%m-%d %X")
		timestamp += timedelta(hours=TIMEZONE_OFFSET) # Account for timezone
		clarification['clarificationTime'] = datetime.strftime(timestamp, "%Y-%m-%d %X")

	# Get list of problems to autocomplete
	problemNames = awstools.problems.getAllProblemNames()

	# List of possible responses to clarifications
	clarificationAnswers = ["Yes", "No", "Answered in task description", "No comment", "Investigating", "Invalid question"]

	form = askClarificationForm()

	if form.is_submitted():
		result = request.form
		form_name = result.get('form_name')
		if form_name == 'askClarification':
			question = result['clarification_question']
			problemName = result['clarification_problem_name']
			if problemName not in problemNames and problemName != "":
				flash("Invalid problem name!","warning")
				return redirect('/clarifications')
			if question == "":
				flash("Question cannot be blank!","warning")
				return redirect('/clarifications')
			awstools.clarifications.createClarification(username=username, problemName=problemName, question=question)
			return redirect('/clarifications')
		elif form_name == 'answerClarification':
			clarificationTime = result.get('clarification_time')
			askedBy = result.get('askedBy')
			answer = result.get('clarification_answer')

			if answer not in clarificationAnswers:
				flash("Invalid Answer!", "warning")
				return redirect("/clarifications")

			if userInfo['role'] != 'admin':
				flash("Admin Access Required!", "warning")
				return redirect("/clarifications")

			# Convert timezone back to UTC
			timestamp = datetime.strptime(clarificationTime, "%Y-%m-%d %X")
			timestamp -= timedelta(hours=TIMEZONE_OFFSET) # Account for timezone
			clarificationTime = datetime.strftime(timestamp, "%Y-%m-%d %X")

			awstools.clarifications.answerClarification(askedBy=askedBy, clarificationTime=clarificationTime, answer=answer, answeredBy=username)
			flash("Clarification Answered", "success")
			return redirect('/clarifications')	
		else: # Catch invalid form
			flash ("An error has occured", "warning")
			return redirect(f'/clarifications')

	return render_template('clarifications.html', userinfo = userInfo, \
		form=form,problemNames=problemNames, clarifications=clarifications, \
		clarificationAnswers = clarificationAnswers)
