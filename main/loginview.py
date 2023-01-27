from flask import render_template, session, redirect, request, flash
import awstools
from forms import LoginForm

def login():
    userinfo = awstools.users.getCurrentUserInfo()

    if userinfo != None:
        flash ("Aready Logged in!", "warning")
        return redirect('/')
    
    form = LoginForm()
    
    if form.is_submitted():
        result = request.form
        username = result['username']
        password = result['password']

        response = awstools.cognito.authenticate(username, password)
        
        if response['status'] != 200: # 403 access denied, 400 error
            flash ('Incorrect password!', 'danger')
            return redirect('/login')

        flash ('Login Success!', 'success')
        
        session['username'] = username
        session.permanent = True

        return redirect('/')
        
    return render_template('login.html', form=form, userinfo=userinfo)

def logout():
    for key in list(session.keys()):
        session.pop(key)

    return redirect('/')
