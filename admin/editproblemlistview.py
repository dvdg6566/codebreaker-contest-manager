from flask import render_template, session, redirect, request, flash
import awstools
from forms import addProblemForm

def editproblemlist():
    userInfo=awstools.users.getCurrentUserInfo()
    problems = awstools.problems.getAllProblemsLimited()
    if userInfo == None or userInfo['role'] != 'admin':
        flash("Admin access is required", "warning")
        return redirect("/")

    problemNames = [P['problemName'] for P in problems]
    
    form = addProblemForm()

    problemScores = {}
    if userInfo != None:
        problemScores = userInfo['problemScores']
    problemInfo = [dict((key,value) for key, value in P.items() if key in ['problemName', 'title', 'source', 'author','problem_type','superhidden','analysisVisible','validated','contestLink','allowAccess']) for P in problems] #impt info goes into the list (key in [list])

    for i in range(len(problemInfo)):
        name = problemInfo[i]['problemName']
        score = 0
        if name in problemScores:
            score = problemScores[name]

        problemInfo[i]['yourScore'] = score

        authors = problemInfo[i]["author"]
        problemInfo[i]["author"] = [x.replace(" ", "") for x in authors.split(",")]
    
    if form.is_submitted():
        result = request.form
        if result['problem_id'] == '':
            flash('Invalid Problem Name', 'warning')
            return redirect('/admin/editproblems')
        if result['problem_id'] in problemNames:
            flash('Problem id already taken', 'warning')
            return redirect('/admin/editproblems')
        awstools.problems.createProblemWithId(result['problem_id'])
        problem_id = result['problem_id']
        return redirect(f'/admin/editproblem/{problem_id}')

    return render_template('editproblemlist.html', form=form, problemInfo=problemInfo, userinfo=userInfo)


