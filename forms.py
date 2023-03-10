from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, BooleanField, SelectField, SubmitField, TextAreaField, PasswordField

class SubmitForm(FlaskForm):
    code = TextAreaField('Code Goes Here')
    codeA = TextAreaField('Code Goes Here')
    codeB = TextAreaField('Code Goes Here')
    language = SelectField('language')
    submit = SubmitField('Submit Code')

class ResubmitForm(FlaskForm):
    code = TextAreaField('Code Goes Here')
    codeA = TextAreaField('Code Goes Here')
    codeB = TextAreaField('Code Goes Here')
    submit = SubmitField('Resubmit')

class LoginForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('name')
    school = StringField('school')
    theme = SelectField('theme')
    hue = DecimalField('hue')
    submit = SubmitField('Save')

class searchSubmissionForm(FlaskForm):
    username = StringField('username')
    problem = StringField('problem')
    submit = SubmitField('Search')

class updateProblemForm(FlaskForm):
    problem_title = StringField('problem_title')
    problem_type = SelectField('problem_type')
    time_limit = DecimalField('time_limit')
    memory_limit = IntegerField('memory_limit')
    feedback = BooleanField('feedback')
    analysis = BooleanField('analysis')
    checker = BooleanField('checker')
    attachments = BooleanField('attachments')
    submit = SubmitField('Update')
    nameA = StringField('nameA')
    nameB = StringField('nameB')

class addProblemForm(FlaskForm):
    problem_id = StringField('problem_id')
    submit = SubmitField('Add Problem')

class beginContestForm(FlaskForm):
    submit = SubmitField('Begin Contest')

class addContestForm(FlaskForm):
    contest_id = StringField('contest_id')
    group_id = StringField('group_id')
    submit = SubmitField('Add Contest')

class updateContestForm(FlaskForm):
    contest_name = StringField('contest_name')
    contest_duration = StringField('contest_duration')
    contest_start = StringField('contest_start')
    contest_end = StringField('contest_end')
    contest_description = TextAreaField('contest_description')
    contest_public = BooleanField('contest_public')
    contest_scoreboardpublic = BooleanField('contest_scoreboardpublic')
    editorial_visible = BooleanField('editorial_visible')
    editorial = StringField('editorial')
    contest_sub_limit = DecimalField('sub_limit')
    contest_sub_delay = DecimalField('sub_delay')
    submit = SubmitField('Update')

class newAnnouncementForm(FlaskForm):
    announcement_title = StringField('announcement_title')
    announcement_text = TextAreaField('announcement_text')
    submit = SubmitField('Submit')  

class askClarificationForm(FlaskForm):
    clarification_question = TextAreaField('clarification_question')
    clarification_problem_name = StringField('clarification_problem_name')
    submit = SubmitField('Add Clarification')

class answerClarificationForm(FlaskForm):
    clarification_answer = SelectField('clarification_answer', choices=['Unanswered', "Yes", "No", "Answered in task description", "No comment", "Investigating", "Invalid question"])
    submit = SubmitField('Answer')
