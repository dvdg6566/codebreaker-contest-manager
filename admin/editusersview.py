from flask import Flask, render_template, request, url_for, redirect, flash, session, get_flashed_messages, make_response, send_file

import json
import awstools
from datetime import datetime

def editUserTable():
    userInfo = awstools.users.getCurrentUserInfo()

    if userInfo == None or userInfo['role'] != 'admin':
        return {'status':300,'error':'Access to resource denied'}

    operation = request.form.get('operation')
    # Adding users to contest
    if operation == 'ADD_USERS_TO_CONTEST':
        contestUsers = json.loads(request.form.get('usernames'))
        contestId = request.form.get('contestId')
        
        contestIds = awstools.contests.getAllContestIds()
        if contestId not in contestIds:
            return {'status':300, 'error': 'Invalid Contest Id!'}

        contestInfo = awstools.contests.getContestInfo(contestId)
        if datetime.utcnow() > contestInfo['endTime']:
            return {'status':300, 'error': 'Contest alrready over!'}

        usernames = [i['username'] for i in awstools.users.getAllUsernames()]
        for user in contestUsers:
            if user not in usernames: return {'status':300, 'error': 'Invalid username!'}

        failusers = awstools.contests.setContest(usernames=contestUsers, contestId=contestId)
        if len(failusers):
            error = "The following users have already began their contest: " + ', '.join(failusers)
            return {'status': 300, 'error': error}

        return {'status': 200}
    elif operation == 'EDIT_USER':
        pass
    else:
        return {'status':300, 'error': 'Invalid operation!'}

def editusers():
    userInfo=awstools.users.getCurrentUserInfo()
    if userInfo == None: return redirect(url_for("login", next=request.url))
    if userInfo['role'] != 'admin': 
        flash("Admin access required!", "warning")
        return redirect("/")

    allUsersInfo = awstools.users.getAllUsers()
    
    contestIds = awstools.contests.getAllContestIds()

    return render_template('editusers.html',userinfo=userInfo,allusersinfo=allUsersInfo,contestIds=contestIds)

