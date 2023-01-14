from flask import flash, render_template, session, request, redirect
import awstools

def home():
	userinfo = awstools.users.getCurrentUserInfo()

	return render_template("home.html", userinfo=userinfo)