from flask import render_template, session, flash, redirect, request
import awstools
from datetime import datetime, timedelta
from forms import addContestForm

def editcontestlist():
    contests = awstools.contests.getAllContests()
    contestNames = [x['contestId'] for x in contests]

    userInfo = awstools.getCurrentUserInfo()

    if userInfo == None:
        return redirect("/login")

    if userInfo['role'] != 'admin':
        flash("Admin access is required", "warning")
        return redirect("/")

    username = userInfo["username"]
    

    if form.is_submitted():
        result = request.form
        if result['form_name'] == 'add_contest':
            if result['contest_id'] == '':
                flash('oopsies! did you accidentally click to add contest?', 'warning')
                return redirect('/admin/editcontests')
            if result['contest_id'] in contestNames:
                flash('oopsies! contest id already taken :(', 'warning')
                return redirect('/admin/editcontests')
            awstools.createContestWithId(result['contest_id'])
            contest_id = result['contest_id']
            return redirect(f'/admin/editcontest/{contest_id}')
        else:
            flash ("An error has occured", "warning")
            return redirect(f'/admin/editcontests')
                
    return render_template('editcontestlist.html', form=form, contestInfos = contestInfos, userinfo=userInfo)
