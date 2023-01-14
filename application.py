import flask
from flask import Flask,session,redirect,send_from_directory,render_template,request,flash
from forms import LoginForm

from waitress import serve

import io
import os

from main import submissionview, profileview, submissionlistview, contestview, contestlistview, scoreboardview, credits, contestgroupview, editprofileview, problemview, announcelistview, announceview, defaultview, clarificationsview, homeview
from admin import adminview, editproblemlistview, editusersview, editproblemview, editcontestlistview, editcontestview, editannouncelistview, editannounceview, editcontestgroupview, editclarificationsview, viewsubmissions, uploadtestdataview
import awstools

# GET ENVIRONMENT VARIABLES
from password import FLASK_SECRET_KEY
# END GET ENVIRONMENT VARIABLES

application = Flask(__name__)

application.config['SECRET_KEY'] = FLASK_SECRET_KEY
application.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 64
application.config['SESSION_COOKIE_SECURE'] = True

application.add_url_rule('/', view_func=homeview.home, methods=["GET"])
application.add_url_rule('/problem/<problemName>', methods=["GET","POST"], view_func=problemview.problem)
application.add_url_rule('/submission/<subId>', view_func = submissionview.submission, methods = ['GET', 'POST'])
application.add_url_rule('/contests', view_func = contestlistview.contestlist)
application.add_url_rule('/contest/<contestId>', view_func = contestview.contest, methods = ['GET', 'POST'])
application.add_url_rule('/contest/<contestId>/scoreboard', view_func = scoreboardview.scoreboard)
application.add_url_rule('/submissions',view_func = submissionlistview.submissionlist, methods=['GET', 'POST'])
application.add_url_rule('/profile/<username>', view_func = profileview.profile)
application.add_url_rule('/admin',view_func=adminview.admin)
application.add_url_rule('/admin/editproblems',view_func=editproblemlistview.editproblemlist, methods = ['GET', 'POST'])
application.add_url_rule('/admin/editusers',view_func=editusersview.editusers)
application.add_url_rule('/admin/edituserrole',view_func=editusersview.editUserRole, methods = ['POST'])
application.add_url_rule('/credits',view_func=credits.credits)
application.add_url_rule('/admin/editproblem/<problemId>', view_func = editproblemview.editproblem, methods = ['GET', 'POST'])
application.add_url_rule('/admin/uploadtestdata/<problemId>', view_func = uploadtestdataview.uploadtestdata, methods = ['GET'])
application.add_url_rule('/admin/editcontests',view_func=editcontestlistview.editcontestlist, methods=['GET', 'POST'])
application.add_url_rule('/admin/editcontest/<contestId>', view_func = editcontestview.editcontest, methods = ['GET', 'POST'])
application.add_url_rule('/admin/editcontestproblems',view_func=editcontestview.editcontestproblems, methods = ['POST'])
application.add_url_rule('/admin/editcontestgroupcontests',view_func=editcontestgroupview.editcontestgroupcontests, methods = ['POST'])
application.add_url_rule('/admin/editcontestgroupgroups',view_func=editcontestgroupview.editcontestgroupgroups,methods=['POST'])
application.add_url_rule('/group/<groupId>', view_func=contestgroupview.contestgroup)
application.add_url_rule('/editprofile', view_func=editprofileview.editprofile, methods=['GET','POST'])
application.add_url_rule('/admin/editannouncements', view_func=editannouncelistview.editannouncelist, methods=['GET','POST'])
application.add_url_rule('/admin/editannouncement/<announceId>', view_func=editannounceview.editannounce, methods=['GET','POST'])
application.add_url_rule('/announcements', view_func=announcelistview.announcelist)
application.add_url_rule('/announcement/<announceId>', view_func=announceview.announce)
application.add_url_rule('/admin/editgroup/<groupId>', view_func=editcontestgroupview.editcontestgroup, methods=['GET','POST'])
application.add_url_rule('/clarifications', view_func=clarificationsview.clarifications, methods=['GET','POST'])
application.add_url_rule('/admin/editclarifications', view_func=editclarificationsview.editclarifications, methods=['GET','POST'])
application.add_url_rule('/admin/viewsubmissions/<problemName>', view_func = viewsubmissions.viewsubmissions, methods=['GET','POST'])

''' BEGIN: AUTHENTICATION WITH AWS COGNITO'''
@application.route('/login', methods=['GET','POST'])
def login():
    userinfo = awstools.users.getCurrentUserInfo()

    if userinfo != None:
        return redirect
    
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
        for key in list(session.keys()):
            session.pop(key)

        session['username'] = username
        session.permanent = True
        return redirect('/')
        
    return render_template('login.html', form=form, userinfo=userinfo)


@application.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)

    return redirect('/')

''' END AUTHENTICATION '''

''' BEGIN CPP REFERENCE '''
def cppref(path):
    return send_from_directory('static/cppreference/reference/en',path)
application.add_url_rule("/cppreference/<path:path>", view_func=cppref)
def cppref2(path):
    return send_from_directory('static/cppreference/reference/common',path)
application.add_url_rule("/common/<path:path>", view_func=cppref2)

''' END CPP REFERENCE '''

app = application

if __name__ == '__main__':
    application.run(debug=True, port=5000)