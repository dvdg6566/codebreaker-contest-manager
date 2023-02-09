import awstools
from flask import Flask, render_template, request, url_for, redirect, flash, session, get_flashed_messages, make_response, send_file

def editUserTable():
    userInfo = awstools.users.getCurrentUserInfo()

    if userInfo == None or userInfo['role'] != 'admin':
        return {'status':300,'error':'Access to resource denied'}

    operation = request.form['operation']
    # Adding users to contest
    if operation == 'ADD_USERS_TO_CONTEST':
        contestUsers = request.form['operation']
        contestId = request.form['operation']

        contestIds = awstools.contests.getAllContestIds()
        usernames = awstools.users.getAllUsernames()
        if contestId not in contestIds: return {'status':300, 'error': 'Invalid contestId!'}
        for user in contestUsers:
            if user not in usernames: return {'status':300, 'error': 'Invalid username!'}

        resp = awstools.user.updateContest(usernames=contestUsers, contestId=contestId)
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
    # allUsersInfo = [dict((key,value) for key, value in U.items() if key in ['username','fullname','school','role', 'nation']) for U in users] #impt info goes into the list (key in [list]) 
    # allUsersInfo = [user for user in allUsersInfo if 'fullname' in user.keys()]
    # allUsersInfo = [user for user in allUsersInfo if user['fullname'] != "" and user['username'] != ""]
    # allUsersInfo.sort(key=lambda x:x['fullname'])

    return render_template('editusers.html',userinfo=userInfo,allusersinfo=allUsersInfo,contestIds=contestIds)

