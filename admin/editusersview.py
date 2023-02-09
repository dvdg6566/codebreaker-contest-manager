import awstools
from flask import Flask, render_template, request, url_for, redirect, flash, session, get_flashed_messages, make_response, send_file

def editUserRole():
    username = request.form['username']
    newrole = request.form['newrole']
    #print(username,newrole)
    userInfo = awstools.getCurrentUserInfo()

    if userInfo == None:
        return {'status':300,'error':'Access to resource denied'}

    if userInfo['role'] != 'admin' and userInfo['role'] != 'superadmin':
        return {'status':300,'error':'Access to resource denied'}

    if newrole not in ['locked', 'disabled', 'member', 'admin']:
        return {'status':301,'error':'Invalid role provided'}

    if userInfo['username'] == username:
        return {'status':302,'error':'Cannot change your own role!'}

    changedUserInfo = awstools.getUserInfoFromUsername(username)
    if changedUserInfo['role'] == 'superadmin':
        return {'status':304,'error':'Cannot de-admin another admin without superadmin privileges!'}

    if changedUserInfo['email'] == None:
        return {'status':303,'error':'User does not exist!'}
    
    if userInfo['role'] != 'superadmin' and changedUserInfo['role'] == 'admin' and newrole != 'admin':
        return {'status':304,'error':'Cannot de-admin another admin without superadmin privileges!'}
    
    awstools.editUserRole(changedUserInfo,newrole,userInfo)
    return {'status':200,'error':''}

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

