from flask import flash, render_template, session, request, redirect
import awstools
from forms import addClarificationForm

def clarifications():

    userInfo = awstools.users.getCurrentUserInfo()
    if userInfo == None:
        flash("Please login to view this page", "warning")
        return redirect("/")
    username = userInfo["username"]

    clarifications = awstools.clarifications.getClarificationsByUser(username)
    clarifications.sort(key=lambda x:x['clarificationId'], reverse=True)

    if contestmode.contest() and contestmode.contestId() != 'analysismirror':
        names = contestmode.contestproblems()

    form = addClarificationForm()

    if form.is_submitted():
        result = request.form
        question = result['clarification_question']
        problemId = result['clarification_problem_id']
        if problemId not in names and problemId != "":
            flash("Invalid problem id!","warning")
            return redirect('/clarifications')
        if question == "":
            flash("Question cannot be blank!","warning")
            return redirect('/clarifications')
        if contestmode.contest() and contestmode.contestId() != 'analysismirror' and problemId == "":
            flash("You cannot make general clarifications in contests!", "warning")
            return redirect('./clarifications')
        awstools.clarifications.createClarification(username, question, problemId)
        return redirect('/clarifications')

    return render_template('clarifications.html', userinfo = userInfo, form=form, clarifications=clarifications)
