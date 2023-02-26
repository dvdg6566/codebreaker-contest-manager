from flask import render_template, session, request, redirect, flash, url_for
from forms import searchSubmissionForm

import os
import awstools
import language
from math import ceil
from datetime import datetime, timedelta

TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET'))
# Convert into specific timezone
def convertToLocalTimezone(timestamp, offset):
	if timestamp == '': return ''
	timestamp += timedelta(hours=offset)
	newTimestring = timestamp.strftime("%Y-%m-%d %X")
	newTimestring += f' (GMT+{offset})' if offset >= 0 else f' (GMT{offset})'
	return newTimestring

def submissionlist():
	pageNo = request.args.get('page')
	username = request.args.get('username')
	problem = request.args.get('problem')
	userInfo = awstools.users.getCurrentUserInfo()

	if userInfo == None: return redirect(url_for("login", next=request.url))
	# ACCESS CONTROL
	if userInfo['role'] == 'member': 
		contestInfo = awstools.contests.getContestInfo(userInfo['contest'])
		if contestInfo == None or contestInfo['status'] != 'ONGOING':
			flash("This resource is only accessible during contests!", "warning")
			return redirect('/')

	# Force redirect back to your own submissions
	if userInfo['role'] == 'member' and userInfo['username'] != username:
		return redirect(f'/submissions?username={userInfo["username"]}&problem={problem if problem else ""}')
	
	if username == "":username = None
	if problem == "":problem = None
	if pageNo == None:pageNo = 1
	pageNo = int(pageNo)

	''' BEGIN: FORMS '''
	form = searchSubmissionForm()
	if form.is_submitted():
		result = request.form
		username = result['username']
		problem = result['problem']
		return redirect(f'/submissions?username={username}&problem={problem}')
	''' END: FORMS '''

	submissionList = []
	maxSub = 0
	
	''' BEGIN: GET ALL SUBMISSIONS TO VIEW '''
	if username == None and problem == None:
		submissionList = awstools.submissions.getSubmissionsList(pageNo, None, None)
		maxSub = int(awstools.submissions.getNumberOfSubmissions())
	else:
		submissionList = awstools.submissions.getSubmissionsList(pageNo, problem, username)
		maxSub = len(submissionList)
	
	subPerPage = awstools.submissions.subPerPage
	submissionList.sort(key = lambda x:x['subId'], reverse=True)

	# Filter away submissions from before contest
	if userInfo['role'] == 'member':
		# submissionList = [submission for submission in submissionList]
		submissionList = [ \
			submission for submission in submissionList \
			if submission['submissionTime'] >= contestInfo['startTime']
		]

	# Conversion of timezone
	for submission in submissionList:
		submission['submissionTime'] = convertToLocalTimezone(submission['submissionTime'], TIMEZONE_OFFSET)

	# If submission is compile error, then max time and memory should be N/A 
	for submission in submissionList:
		if 'compileErrorMessage' in submission.keys():
			submission['maxTime'] = 'N/A'
			submission['maxMemory'] = 'N/A'

	# Pagination
	if username != None or problem != None:
		submissionList = submissionList[(pageNo-1)*subPerPage : min(len(submissionList), pageNo*subPerPage)]

	maxPage = ceil(maxSub / subPerPage)
	pages = range(max(1, pageNo-1), min(maxPage+1, pageNo+3)) 
	  
	linkname = 'submissions?'
	if username != None:
		linkname += f'username={username}&'
	if problem != None:
		linkname += f'problem={problem}&'

	# Converts languages back to their original full form
	languages_inverse = language.get_languages_inverse()
	for i in submissionList:
		i['language'] = languages_inverse[i['language']]

	# Consolidated data based on query
	info = {
		'submissionList':submissionList,
		'pageNo': pageNo,
		'pages': pages,
		'maxPage': maxPage,
		'linkname': linkname,
		'username': '' if username == None else username,
		'problem': '' if problem == None else problem
	}

	return render_template('submissionlist.html', form=form, userinfo=userInfo, info=info)
