from flask import render_template, session, flash, redirect, request
from forms import addContestForm

import os
import awstools
from datetime import datetime, timedelta

# Gets timezone from environment variables
TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET'))

def editcontesttimes():
	contestId = request.form['contestId']

	# Authenticate
	userInfo = awstools.users.getCurrentUserInfo()
	if userInfo == None or userInfo['role'] != 'admin': 
		return {'status':300,'error':'Access to resource denied'}

	startTime = request.form['startTime']
	endTime = request.form['endTime']

	try:
		startTime = datetime.strptime(startTime, "%Y-%m-%d %X")
		endTime = datetime.strptime(endTime, "%Y-%m-%d %X")
	except ValueError:
		return {'status':300, 'error':'Invalid datetime format'}

	# Convert Start and end time from local time to GMT time
	startTime -= timedelta(hours=TIMEZONE_OFFSET)
	endTime -= timedelta(hours=TIMEZONE_OFFSET)

	# Check that endTime has not already passed
	if endTime < datetime.utcnow():
		return {'status':300, 'error': 'Cannot set contest to end in the past!'}

	params = {
		'startTime': str(startTime),
		'endTime': str(endTime) 
	}

	awstools.contests.updateContestTable(contestId, params)
	return {'status':200}

def editcontestlist():
	userInfo = awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect("/login")
	if userInfo['role'] != 'admin':
		flash("Admin access is required", "warning")
		return redirect("/")

	contestsInfo = awstools.contests.getAllContestInfo()
	contestNames = [x['contestId'] for x in contestsInfo]

	# Fill up which user in contest
	usersInfo = awstools.users.getAllUserContests()
	contestUsers = {}
	for i in contestNames: contestUsers[i] = []
	for user in usersInfo: 
		if user['contest'] in contestUsers:
			contestUsers[user['contest']].append(user['username'])

	for contest in contestsInfo:
		contest['users'] = contestUsers[contest['contestId']]
		
		# Convert Start and end time from GMT time to local time
		contest['startTime'] += timedelta(hours=TIMEZONE_OFFSET)
		contest['endTime'] += timedelta(hours=TIMEZONE_OFFSET)
		contest['duration'] = str(contest['endTime'] - contest['startTime'])
		contest['startTime'] = str(contest['startTime'])
		contest['endTime'] = str(contest['endTime'])
		contest['problems'] = ['addition', 'multiplication', 'test', 'test2']

	# Timezone string formatted to show GMT
	timezoneString = f'+{TIMEZONE_OFFSET}' if TIMEZONE_OFFSET >= 0 else f'{TIMEZONE_OFFSET}'
	
	form = addContestForm()

	if form.is_submitted():
		result = request.form
		if result['form_name'] == 'add_contest':
			if result['contest_id'] == '':
				flash('Invalid Contest Id!', 'warning')
				return redirect('/admin/editcontests')
			if result['contest_id'] in contestNames:
				flash('Contest Id already taken!', 'warning')
				return redirect('/admin/editcontests')
			contestId = result['contest_id']
			awstools.contests.createContest(contestId)
			return redirect(f'/admin/editcontest/{contestId}')
		else: # Catch invalid form
			flash ("An error has occured", "warning")
			return redirect(f'/admin/editcontests')
				
	return render_template('editcontestlist.html', form=form, contestsInfo = contestsInfo, userinfo=userInfo, timezoneOffset=timezoneString)
