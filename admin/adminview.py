from flask import render_template, session, url_for, redirect, flash

import awstools

def admin():
    # Put this before every admin page lol
    userInfo=awstools.users.getCurrentUserInfo()
    if userInfo == None or userInfo['role'] != 'admin':
        flash("Admin access is required", "warning")
        return redirect("/")

    return render_template('admin.html',userinfo=userInfo)

