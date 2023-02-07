from flask import flash, render_template, session, request, redirect, url_for
import awstools
from forms import addClarificationForm

def clarifications():
	userInfo=awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect(url_for("login", next=request.url))

	username = userInfo['username']

	# Get list of clarifications to display
	if userInfo['role'] == 'admin':
		clarifications = awstools.clarifications.getAllClarifications()
		clarifications.sort(key=lambda x:x['clarificationTime'], reverse=True)
	else:
		clarifications = awstools.clarifications.getClarificationsByUser(username=username)

	# Get list of problems to autocomplete
	problemNames = awstools.problems.getAllProblemNames()

	# List of possible responses to clarifications
	clarificationAnswers = ["Yes", "No", "Answered in task description", "No comment", "Investigating", "Invalid question"]

	form = addClarificationForm()

	if form.is_submitted():
		result = request.form
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

	return render_template('clarifications.html', userinfo = userInfo, form=form, problemNames=problemNames, clarifications=clarifications, clarificationAnswers=clarificationAnswers)
