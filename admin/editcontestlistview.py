import os
import awstools
from forms import addContestForm
from datetime import datetime, timedelta
from flask import render_template, session, flash, redirect, request

# Gets timezone from environment variables
TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET'))

def editcontesttable():
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

	params = {
		'contestName': request.form['contestName'],
		'description': request.form['description'],
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
	for contest in contestsInfo:
		contest['startTime'] = datetime.strptime(contest['startTime'], "%Y-%m-%d %X")
		contest['endTime'] = datetime.strptime(contest['endTime'], "%Y-%m-%d %X")

		# Convert Start and end time from GMT time to local time
		contest['startTime'] += timedelta(hours=TIMEZONE_OFFSET)
		contest['endTime'] += timedelta(hours=TIMEZONE_OFFSET)
		contest['duration'] = str(contest['endTime'] - contest['startTime'])
		contest['startTime'] = str(contest['startTime'])
		contest['endTime'] = str(contest['endTime'])
		contest['problems'] = ['addition', 'multiplication', 'test', 'test2']

	contestNames = [x['contestId'] for x in contestsInfo]

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
