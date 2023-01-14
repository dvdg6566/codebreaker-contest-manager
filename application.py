import flask
from flask import Flask,session,redirect, send_from_directory,request,jsonify

from waitress import serve

import io
import sys
import json
from password import FLASK_SECRET_KEY, GOOGLE_CLIENT_SECRET, AWS_COGNITO_USER_POOL_CLIENT_SECRET
from pytz import utc

from main import submissionview, newuserview, profileview, submissionlistview, contestview, contestlistview, scoreboardview, credits, contestgroupview, editprofileview, problemview, announcelistview, announceview, defaultview, clarificationsview
from admin import adminview, editproblemlistview, editusersview, editproblemview, editcontestlistview, editcontestview, editannouncelistview, editannounceview, editcontestgroupview, editclarificationsview, viewsubmissions, uploadtestdataview
import awstools
from datetime import datetime,timedelta

from flask_awscognito import AWSCognitoAuthentication

application = Flask(__name__)

application.config['SECRET_KEY'] = FLASK_SECRET_KEY
application.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 64
application.config['SESSION_COOKIE_SECURE'] = True

application.add_url_rule("/problem/<problemName>", methods=["GET","POST"], view_func=problemview.problem)
application.add_url_rule('/submission/<subId>', view_func = submissionview.submission, methods = ['GET', 'POST'])
application.add_url_rule('/contests', view_func = contestlistview.contestlist)
application.add_url_rule('/contest/<contestId>', view_func = contestview.contest, methods = ['GET', 'POST'])
application.add_url_rule('/contest/<contestId>/scoreboard', view_func = scoreboardview.scoreboard)
application.add_url_rule('/submissions',view_func = submissionlistview.submissionlist, methods=['GET', 'POST'])
application.add_url_rule('/newuser', view_func = newuserview.newuser, methods = ['GET', 'POST'])
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

'''  BEGIN CONFIGURATION FOR AWS'''
application.config['AWS_DEFAULT_REGION'] = 'ap-southeast-1'
application.config['AWS_COGNITO_DOMAIN'] = 'https://codebreaker.auth.ap-southeast-1.amazoncognito.com'
application.config['AWS_COGNITO_USER_POOL_ID'] = 'ap-southeast-1_xiTNBPfQ3'
application.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '1uaqgoe5d81nr05hchuq7uf1s'
application.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = AWS_COGNITO_USER_POOL_CLIENT_SECRET
application.config['AWS_COGNITO_REDIRECT_URL'] = 'http://localhost:5050/aws_cognito_redirect'
    
aws_auth = AWSCognitoAuthentication(application)

@application.route('/')
@aws_auth.authentication_required
def index():
    claims = aws_auth.claims # also available through g.cognito_claims
    return jsonify({'claims': claims})

# Cognito redirect is the link passed into AWS cognito
# It tells cognito where to redirect users after login is complete

@application.route('/aws_cognito_redirect')
def aws_cognito_redirect():
    # Basically u take the request.args to use it (one time only) to get access token
    # Then u store the access token in session to persist it

    # Remove any session information already present
    for key in list(session.keys()):
        session.pop(key)

    access_token = aws_auth.get_access_token(request.args)
    username = awstools.cognito.getUserInfo(accessToken=access_token)

    session['username'] = username
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed

    return redirect('/problem/helloworld')
    # return redirect somewhere

# Sign is is the route to send users to go to cognito
@application.route('/login')
def login():
    return redirect(aws_auth.get_sign_in_url())

@application.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)

    return redirect('/problem/helloworld')

''' END AUTHENTICATION '''

''' BEGIN CPP REFERENCE '''
def cppref(path):
    return send_from_directory('static/cppreference/reference/en',path)
application.add_url_rule("/cppreference/<path:path>", view_func=cppref)
def cppref2(path):
    return send_from_directory('static/cppreference/reference/common',path)
application.add_url_rule("/common/<path:path>", view_func=cppref2)

''' END CPP REFERENCE '''

if __name__ == '__main__':
    application.run(debug=True, port=5000)