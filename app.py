import flask
from flask import Flask,session,redirect,send_from_directory,render_template,request,flash
from forms import LoginForm

from waitress import serve

import io
import os

# Loads environment variables using dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from main import submissionview, profileview, submissionlistview, credits, problemview, announcelistview, clarificationsview, homeview, loginview
from admin import adminview, editproblemlistview, editusersview, editproblemview, editcontestlistview, editcontestview, editclarificationsview, uploadtestdataview
import awstools

app = Flask(__name__)

FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 64
app.config['SESSION_COOKIE_NAME'] = 'codebreaker-login'

app.add_url_rule('/', view_func=homeview.home, methods=["GET"])
app.add_url_rule('/problem/<problemName>', methods=["GET","POST"], view_func=problemview.problem)
app.add_url_rule('/submission/<subId>', view_func = submissionview.submission, methods = ['GET', 'POST'])
# app.add_url_rule('/contest/<contestId>/scoreboard', view_func = scoreboardview.scoreboard)
app.add_url_rule('/submissions',view_func = submissionlistview.submissionlist, methods=['GET', 'POST'])
app.add_url_rule('/profile/<username>', view_func = profileview.profile)
app.add_url_rule('/admin',view_func=adminview.admin)
app.add_url_rule('/admin/editproblems',view_func=editproblemlistview.editproblemlist, methods = ['GET', 'POST'])
app.add_url_rule('/admin/editusers',view_func=editusersview.editusers)
app.add_url_rule('/admin/edituserrole',view_func=editusersview.editUserRole, methods = ['POST'])
app.add_url_rule('/credits',view_func=credits.credits)
app.add_url_rule('/admin/editproblem/<problemId>', view_func = editproblemview.editproblem, methods = ['GET', 'POST'])
app.add_url_rule('/admin/uploadtestdata/<problemId>', view_func = uploadtestdataview.uploadtestdata, methods = ['GET'])
app.add_url_rule('/admin/editcontests',view_func=editcontestlistview.editcontestlist, methods=['GET', 'POST'])
app.add_url_rule('/admin/editcontesttable', view_func=editcontestlistview.editcontesttable, methods=['POST'])
app.add_url_rule('/admin/editcontest/<contestId>', view_func = editcontestview.editcontest, methods = ['GET', 'POST'])
app.add_url_rule('/admin/editcontestproblems',view_func=editcontestview.editcontestproblems, methods = ['POST'])
app.add_url_rule('/announcements', view_func=announcelistview.announcelist, methods=['GET','POST'])
app.add_url_rule('/clarifications', view_func=clarificationsview.clarifications, methods=['GET','POST'])
app.add_url_rule('/admin/editclarifications', view_func=editclarificationsview.editclarifications, methods=['GET','POST'])
app.add_url_rule('/login', view_func=loginview.login, methods = ['GET', 'POST'])
app.add_url_rule('/logout', view_func=loginview.logout, methods = ['GET'])

''' BEGIN CPP REFERENCE '''
def cppref(path):
    return send_from_directory('static/cppreference/reference/en',path)
app.add_url_rule("/cppreference/<path:path>", view_func=cppref)
def cppref2(path):
    return send_from_directory('static/cppreference/reference/common',path)
app.add_url_rule("/common/<path:path>", view_func=cppref2)

''' END CPP REFERENCE '''
if __name__ == '__main__':
    app.run(debug=True, port=5000)

    # awstools.cognito.createUser('sgzoo2', 'singaporezoo060@gmail.com', 'admin')