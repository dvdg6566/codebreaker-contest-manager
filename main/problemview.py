import io
import time
import random
import flask
import awstools
from forms import SubmitForm
from compilesub import check
from flask import Flask, render_template, request, url_for, redirect, flash, session, get_flashed_messages, make_response, send_file
from language import get_languages
languages = get_languages()

def problem(problemName):

    userInfo = awstools.users.getCurrentUserInfo()

    # TODO: Do authentication on whether user allowed to view problem

    scores = []
    verdicts = []
    returnCodes = []
    maxTime = []
    maxMemory = []
    t = 0
    t = time.time()
    form = SubmitForm()

    form.language.choices = list(languages.keys())
        
    problemInfo = awstools.problems.getProblemInfo(problemName)
    if (type(problemInfo) is str):
        return 'Sorry, this problem does not exist'
    problemInfo['testcaseCount'] = int(problemInfo['testcaseCount'])
    timeLimit = problemInfo['timeLimit']
    memoryLimit = problemInfo['memoryLimit']
    subtaskMaxScores = problemInfo['subtaskScores']
    subtaskNumber = len(subtaskMaxScores)
    subtaskDependency = problemInfo['subtaskDependency']
    testcaseNumber = problemInfo['testcaseCount']
    customChecker = problemInfo['customChecker']
    source = problemInfo['source']
    author = problemInfo['author']
    problemInfo["author"] = [x.replace(" ", "") for x in author.split(",")]
    title = problemInfo['title']
    analysisVisible = problemInfo['analysisVisible']
    problemType = problemInfo['problem_type']
    validated = problemInfo['validated']

    if problemInfo['problem_type'] == 'Communication':
        if 'nameA' not in problemInfo.keys():
            problemInfo['nameA'] = 'placeholderA'
        if 'nameB' not in problemInfo.keys():
            problemInfo['nameB'] = 'placeholderB'
    
    if not validated:
        if (userInfo == None or (userInfo['role'] != 'admin' and userInfo['role'] != 'superadmin')):
            flash("Sorry, this problem still has issues. Please contact the administrators.", 'warning')
            return redirect("/")
        else:
            canSubmit = False
            flash("Problem has 1 or more issues that require fixing",'danger')

    # Gets both HTML and PDF problem statement
    result = awstools.problems.getProblemStatementHTML(problemName)

    if result['status'] == 200:
        statementHTML = result['response']
    else:  # No statement found
        flash("Statement not found", "warning")
        statementHTML = ""

    delay = 9
    outlets = 15

    if form.is_submitted():
        result = request.form
        
        if 'form_name' in result and result['form_name'] == 'download_input':
            if userInfo == None or userInfo['role'] != 'admin':
                flash('You do not have permission to access this resource!','warning')
                return redirect(f'/problem/{problemName}')
            tcno = result['tcin']
            filename=f'{problemName}/{tcno}.in'
            tcfile = awstools.problems.getTestcase(filename)
            mem = io.BytesIO()
            mem.write(tcfile.encode('utf-8'))
            mem.seek(0)
            return send_file(mem,as_attachment=True,attachment_filename=filename)

        elif 'form_name' in result and result['form_name'] == 'download_output':
            if userInfo == None or (userInfo['role'] != 'admin' and userInfo['role'] != 'superadmin'):
                flash('You do not have permission to access this resource!','warning')
                return redirect(f'/problem/{problemName}')
            if userInfo == None or userInfo['role'] != 'admin':
                flash('You do not have permission to access this resource!', 'warning')
                return redirect(f'/problem{problemName}')
            tcno = result['tcout']
            filename=f'{problemName}/{tcno}.out'
            tcfile = awstools.problems.getTestcase(filename)
            mem = io.BytesIO()
            mem.write(tcfile.encode('utf-8'))
            mem.seek(0)
            return send_file(mem,as_attachment=True,attachment_filename=filename)

        elif 'form_name' in result and result['form_name'] == 'download_attachment':
            filename=f'{problemName}.zip';
            zipfile=awstools.problems.getAttachment(filename)
            return send_file(zipfile, as_attachment=True, attachment_filename=filename)

        # Checking for language
        language = 'C++ 17'
        if 'language' in result:
            language = result['language']
        if language not in languages.keys(): # Invalid language
            flash('Invalid language!', 'warning')
            return redirect(f'/problem/{problemName}')
        language = languages[language]

        ''' BLOCK DISABLED OR NON-USERS FROM SUBMITTING '''
        if userInfo == None or (userInfo['role'] not in ['member','admin','superadmin']):
            flash('You do not have permission to submit!','warning')
            return redirect(f'/problem/{problemName}')
        
        # COMPILE AND GRADE COMMUNICATION PROBLEM
        if problemInfo['problem_type'] == 'Communication':
            codeA = result['codeA']
            codeB = result['codeB']

            checkResult = check(codeA, problemInfo, userInfo)
            if checkResult["status"] != "success":
                status = checkResult["status"]
                message = checkResult["message"]
                flash(message, status)

                if status == "danger":
                    return redirect(f"/problem/{problemName}")
            
                if status == "warning":
                    return redirect("/")

            checkResult = check(codeB, problemInfo, userInfo)
            if checkResult["status"] != "success":
                status = checkResult["status"]
                message = checkResult["message"]
                flash(message, status)

                if status == "danger":
                    return redirect(f"/problem/{problemName}")
            
                if status == "warning":
                    return redirect("/")

            # Assign new submission index
            subId = awstools.submissions.getNextSubmissionId()

            # Upload code file to S3
            s3pathA = f'source/{subId}A.{language}'
            s3pathB = f'source/{subId}B.{language}'
            awstools.submissions.uploadSubmission(code = codeA, s3path = s3pathA)
            awstools.submissions.uploadSubmission(code = codeB, s3path = s3pathB)

        else:
        # COMPILE AND GRADE BATCH OR INTERACTIVE PROBLEM 
            code = result['code']
            checkResult = check(code, problemInfo, userInfo)

            if checkResult["status"] != "success":
                status = checkResult["status"]
                message = checkResult["message"]
                flash(message, status)

                if status == "danger":
                    return redirect(f"/problem/{problemName}")
            
                if status == "warning":
                    return redirect("/")

            # Assign new submission index
            subId = awstools.submissions.getNextSubmissionId()

            # Upload code file to S3
            s3path = f'source/{subId}.{language}'
            awstools.submissions.uploadSubmission(code = code, s3path = s3path)

        # Grade submission
        awstools.submissions.gradeSubmission(
            problemName = problemName,
            submissionId = subId,
            username = userInfo['username'], 
            submissionTime = None,
            regradeall=False,
            language = language,
            problemType = problemInfo['problem_type']
        )

        time.sleep(2)
        return redirect(f"/submission/{subId}")

    return render_template('problem.html', form=form, probleminfo=problemInfo, userinfo = userInfo, statementHTML = statementHTML, remsubs = 50)
    
