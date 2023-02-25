from flask import render_template, session, redirect, request, flash
from forms import LoginForm

import awstools

def login():
    userinfo = awstools.users.getCurrentUserInfo()

    if userinfo != None:
        flash ("Aready Logged in!", "warning")
        return redirect('/')
    
    form = LoginForm()
    
    if form.is_submitted():
        result = request.form
        username = request.form.get("username")
        password = request.form.get("password")
        next_url = request.form.get("next")

        response = awstools.cognito.authenticate(username, password)
        
        if response['status'] != 200: # 403 access denied, 400 error
            flash ('Incorrect password!', 'danger')
            return redirect('/login')

        flash ('Login Success!', 'success')
        
        session['username'] = username
        session.permanent = True

        if next_url:
            return redirect(next_url)
        return redirect('/')
        
    return render_template('login.html', form=form, userinfo=userinfo)

def logout():
    for key in list(session.keys()):
        session.pop(key)

    return redirect('/')
