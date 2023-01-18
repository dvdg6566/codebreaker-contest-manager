from flask import render_template, session, redirect
import awstools

def profile(username):    
    profileinfo = awstools.users.getUserInfo(username)
    userInfo = awstools.users.getCurrentUserInfo()

    if profileinfo == None or profileinfo['username'] == "":
        return "Sorry this user doesn't exist"

    return render_template('profile.html', profileinfo=profileinfo, userinfo=userInfo)

