from flask import render_template, session, request, redirect, flash, url_for
from forms import searchSubmissionForm
import awstools
import language
from math import ceil
from pprint import pprint

def submissionlist():
    pageNo = request.args.get('page')
    username = request.args.get('username')
    problem = request.args.get('problem')
    userInfo = awstools.users.getCurrentUserInfo()

    if userInfo == None: return redirect(url_for("login", next=request.url))

    # Force redirect back to your own submissions
    if userInfo['role'] == 'member' and userInfo['username'] != username:
        return redirect(f'/submissions?username={userInfo["username"]}&problem={problem if problem else ""}')
    
    if username == "":username = None
    if problem == "":problem = None
    if pageNo == None:pageNo = 1
    pageNo = int(pageNo)

    ''' BEGIN: FORMS '''
    form = searchSubmissionForm()
    if form.is_submitted():
        result = request.form
        username = result['username']
        problem = result['problem']
        return redirect(f'/submissions?username={username}&problem={problem}')
    ''' END: FORMS '''

    submissionList = []
    maxSub = 0
    
    ''' BEGIN: GET ALL SUBMISSIONS TO VIEW '''
    if username == None and problem == None:
        submissionList = awstools.submissions.getSubmissionsList(pageNo, None, None)
        maxSub = int(awstools.submissions.getNumberOfSubmissions())
    else:
        submissionList = awstools.submissions.getSubmissionsList(pageNo, problem, username)
        maxSub = len(submissionList)
    print(maxSub)
    
    subPerPage = awstools.submissions.subPerPage
    submissionList.sort(key = lambda x:x['subId'], reverse=True)
    if username != None or problem != None:
        submissionList = submissionList[(pageNo-1)*subPerPage : min(len(submissionList), pageNo*subPerPage)]

    # If submission is compile error, then max time and memory should be N/A 
    for submission in submissionList:
        if 'compileErrorMessage' in submission.keys():
            submission['maxTime'] = 'N/A'
            submission['maxMemory'] = 'N/A'

    maxPage = ceil(maxSub / subPerPage)
    pages = range(max(1, pageNo-1), min(maxPage+1, pageNo+3)) 
      
    linkname = 'submissions?'
    if username != None:
        linkname += f'username={username}&'
    if problem != None:
        linkname += f'problem={problem}&'

    # Converts languages back to their original full form
    languages_inverse = language.get_languages_inverse()
    for i in submissionList:
        i['language'] = languages_inverse[i['language']]

    # Consolidated data based on query
    info = {
        'submissionList':submissionList,
        'pageNo': pageNo,
        'pages': pages,
        'maxPage': maxPage,
        'linkname': linkname,
        'username': '' if username == None else username,
        'problem': '' if problem == None else problem
    }

    return render_template('submissionlist.html', form=form, userinfo=userInfo, info=info)
