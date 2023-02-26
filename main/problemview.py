from flask import Flask, render_template, request, url_for, redirect, flash, session, get_flashed_messages, make_response, send_file
from forms import SubmitForm

import io
import awstools
from time import sleep 

from language import get_languages
languages = get_languages()

def problem(problemName):
	userInfo = awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect(url_for("login", next=request.url))

	# ACCESS CONTROL
	if userInfo['role'] == 'member': 
		contestInfo = awstools.contests.getContestInfo(userInfo['contest'])
		if contestInfo == None or contestInfo['status'] != 'ONGOING':
			flash("This resource is only accessible during contests!", "warning")
			return redirect('/')

	form = SubmitForm()

	form.language.choices = list(languages.keys())
		
	problemInfo = awstools.problems.getProblemInfo(problemName)
	if (type(problemInfo) is str):
		return 'Sorry, this problem does not exist'
	problemInfo['testcaseCount'] = int(problemInfo['testcaseCount'])

	if problemInfo['problem_type'] == 'Communication':
		if 'nameA' not in problemInfo.keys():
			problemInfo['nameA'] = 'placeholderA'
		if 'nameB' not in problemInfo.keys():
			problemInfo['nameB'] = 'placeholderB'
	
	if not problemInfo['validated']:
		if (userInfo == None or (userInfo['role'] != 'admin' and userInfo['role'] != 'superadmin')):
			flash("Sorry, this problem still has issues. Please contact the administrators.", 'warning')
			return redirect("/")
		else:
			canSubmit = False
			flash("Problem has 1 or more issues that require fixing",'danger')

	# Gets both HTML and PDF problem statement
	result = awstools.problems.getProblemStatementHTML(problemName)

	if result['status'] == 200:
		statementHTML = result['response']
	else:  # No statement found
		flash("Statement not found", "warning")
		statementHTML = ""

	if form.is_submitted():
		result = request.form
		if userInfo == None:
			flash("Unauthorised access!", "warning")
			return redirect(f'/problem/{problemName}')
		
		if 'form_name' in result and result['form_name'] in ['download_input', 'download_output']:
			if userInfo == None or userInfo['role'] != 'admin':
				flash('You do not have permission to access this resource!','warning')
				return redirect(f'/problem/{problemName}')
			if result['form_name'] == 'download_input': 
				tcno = result['tcin']
				filename=f'{problemName}/{tcno}.in'
			else: 
				tcno = result['tcout']
				filename=f'{problemName}/{tcno}.out'
			tcfile = awstools.problems.getTestcase(filename)
			mem = io.BytesIO()
			mem.write(tcfile.encode('utf-8'))
			mem.seek(0)
			return send_file(mem,as_attachment=True,download_name=filename)

		elif 'form_name' in result and result['form_name'] == 'download_attachment':
			filename=f'{problemName}.zip';
			zipfile=awstools.problems.getAttachment(filename)
			return send_file(zipfile, as_attachment=True, attachment_filename=filename)

		# Checking for language
		language = 'C++ 17'
		if 'language' in result:
			language = result['language']
		if language not in languages.keys(): # Invalid language
			flash('Invalid language!', 'warning')
			return redirect(f'/problem/{problemName}')
		language = languages[language]

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

		sleep(2)
		return redirect(f"/submission/{response['subId']}")

	return render_template('problem.html', form=form, probleminfo=problemInfo, userinfo = userInfo, statementHTML = statementHTML, remsubs = 50)
	