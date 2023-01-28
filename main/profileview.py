from flask import render_template, session, redirect
import awstools

def profile(username):    
	profileinfo = awstools.users.getUserInfo(username)
	userInfo = awstools.users.getCurrentUserInfo()

	if userInfo == None: return redirect(url_for("login", next=request.url))

	if userInfo['role'] != 'admin':
		flash("Admin access is required", "warning")
		return redirect('/')

	if profileinfo == None or username == "":
		flash("Sorry this user doesn't exist", "warning")
		return redirect('/')

	return render_template('profile.html', profileinfo=profileinfo, userinfo=userInfo)

