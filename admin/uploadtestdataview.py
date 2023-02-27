from flask import Flask, render_template, request, url_for, redirect, flash, session, get_flashed_messages, make_response, send_file

import os
import json
import awstools

# Gets judgename, region from environment variables
judgeName = os.environ.get('JUDGE_NAME')
AWS_REGION = os.environ.get('AWS_REGION')

def uploadtestdata(problemId):
	userInfo = awstools.users.getCurrentUserInfo()
	problemInfo = awstools.problems.getProblemInfo(problemId)

	if problemInfo == None:
		flash('This problem does not exist', 'warning')
		return redirect('/admin')

	if userInfo == None or userInfo['role'] != 'admin':
		flash ('You are not authorised to view this resource!', 'danger')
		return redirect('/')

	credentials = awstools.sts.getTokens(problemId)
	credentials['bucketName'] = f'{judgeName}-testdata'
	credentials['bucketRegion'] = f'{AWS_REGION}'
	credentials = json.dumps(credentials)

	return render_template('uploadtestdata.html', userinfo=userInfo, probleminfo=problemInfo, stsKeys=credentials)