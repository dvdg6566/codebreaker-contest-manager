from flask import flash, render_template, session, request, redirect
from forms import updateProblemForm

import json
import awstools
import subprocess

def verifyDependency(dependency):
    ranges = dependency.split(',')
    for i in ranges:
        nums = i.split('-')
        if len(nums) > 2:
            return False
        elif len(nums) > 1:
            x, y = int(nums[0]), int(nums[1])
            if (x > y):
                return False
    return True

def editproblem(problemName):
    userInfo = awstools.users.getCurrentUserInfo()
    if userInfo == None: return redirect("/login")
    if userInfo['role'] != 'admin':
        flash("Admin access is required", "warning")
        return redirect("/")
    
    problemInfo = awstools.problems.getProblemInfo(problemName)
    if problemInfo == None:
        flash ('Sorry, this problem does not exist', 'warning')
        return redirect("/admin/editproblems")

    if problemInfo['problem_type'] == 'Interactive':
        if 'nameA' not in problemInfo.keys():
            problemInfo['nameA'] = 'placeholderA'
        if 'nameB' not in problemInfo.keys():
            problemInfo['nameB'] = 'placeholderA'

    form = updateProblemForm()
    form.problem_type.choices = ["Batch", "Communication", "Interactive"]
    form.problem_type.choices.remove(problemInfo['problem_type'])
    form.problem_type.choices.insert(0,problemInfo['problem_type'])

    if form.is_submitted():
        result = request.form
        files = request.files

        if result['form_name'] == 'problem_info':
            info = {}
            info['title'] = result['problem_title']
            info['problem_type'] = result['problem_type']
            info['timeLimit'] = result['time_limit']
            info['memoryLimit'] = result['memory_limit']
            info['attachments'] = ('attachments' in result)
            info['customChecker'] = ('checker' in result)
            info['fullFeedback'] = ('feedback' in result)

            if 'nameA' in result.keys():
                info['nameA'] = result['nameA']
            if 'nameB' in result.keys():
                info['nameB'] = result['nameB']

            awstools.problems.updateProblemInfo(problemName, info)
            if problemInfo['problem_type'] == 'Communication':
                awstools.problems.updateCommunicationFileNames(problemName,info)
            awstools.problems.validateProblem(f'{problemName}')
            return redirect(f'/admin/editproblem/{problemName}')
        
        elif result['form_name'] == 'statement_upload':
            if 'statement' not in files:
                flash('Statement not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            if files['statement'].filename == '':
                flash('Statement not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            file_name = files['statement'].filename
            if '.' not in file_name:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            ext_file = file_name.rsplit('.', 1)[1].lower()
            if ext_file in ['pdf', 'html']:
                awstools.problems.uploadStatement(files['statement'], f'{problemName}.{ext_file}')
                flash('Uploaded!', 'success')
                awstools.problems.validateProblem(f'{problemName}')
                return redirect(f'/admin/editproblem/{problemName}')
            else:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'delete_html':
            awstools.problems.deleteStatement(f'{problemName}.html')
            flash('HTML statement deleted!', 'success')
            awstools.problems.validateProblem(f'{problemName}')
            return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'delete_pdf':
            awstools.problems.deleteStatement(f'{problemName}.pdf')
            flash('PDF statement deleted!', 'success')
            awstools.problems.validateProblem(f'{problemName}')
            return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'validate':
            awstools.problems.validateProblem(f'{problemName}')
            flash('Validated problem!','success')
            return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'add_subtask':
            problemInfo['subtaskScores'].append(0)
            problemInfo['subtaskDependency'].append('1')
            info = {}
            info['subtaskScores'] = problemInfo['subtaskScores']
            info['subtaskDependency'] = problemInfo['subtaskDependency']
            awstools.problems.updateSubtaskInfo(problemName, info)
            return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'remove_subtask':
            if len(problemInfo['subtaskScores']) == 1:
                flash('hisssss! cannot have less than one subtask', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            problemInfo['subtaskScores'].pop()
            problemInfo['subtaskDependency'].pop()
            info = {}
            info['subtaskScores'] = problemInfo['subtaskScores']
            info['subtaskDependency'] = problemInfo['subtaskDependency']
            awstools.problems.updateSubtaskInfo(problemName, info)
            return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'update_subtask':
            info = {}
            info['subtaskScores'] = []
            info['subtaskDependency'] = []
            i = 0
            total = 0
            while ('sc_' + str(i)) in result:
                score = int(result['sc_' + str(i)])
                info['subtaskScores'].append(score)
                total += score
                dep = result['dp_' + str(i)]
                dep = dep.replace(" ","")
                if not verifyDependency(dep):
                    flash('Invalid subtask dependency', 'warning')
                    return redirect(f'/admin/editproblem/{problemName}')
                info['subtaskDependency'].append(dep)
                i += 1
            if total > 100:
                flash('Total score cannot be more than 100!', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            awstools.problems.updateSubtaskInfo(problemName, info)
            awstools.problems.validateProblem(f'{problemName}')
            return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'checker_upload':
            # Compiling C++ custom checker
            if 'checker' not in files:
                flash('Statement not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            if files['checker'].filename == '':
                flash('Checker not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            file_name = files['checker'].filename
            if '.' not in file_name:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            ext_file = file_name.rsplit('.', 1)[1].lower()
            if ext_file == 'cpp':
                awstools.problems.uploadChecker(files['checker'], f'source/{problemName}.cpp')
                response = awstools.problems.compileChecker(problemName = problemName)

                if response['status'] == 200:
                    flash('Uploaded!', 'success')
                    awstools.problems.validateProblem(f'{problemName}')
                    return redirect(f'/admin/editproblem/{problemName}')
                else:
                    flash(response['error'], 'warning')
                    return redirect(f'/admin/editproblem/{problemName}')
            else:
                flash('Invalid language', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'grader_upload':
            # grader.cpp file for interactive/communication problems
            if 'grader' not in files:
                flash('Grader not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            if files['grader'].filename == '':
                flash('Grader not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            file_name = files['grader'].filename
            if '.' not in file_name:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            ext_file = file_name.rsplit('.', 1)[1].lower()
            if ext_file == 'cpp':
                awstools.problems.uploadGrader(files['grader'], f'{problemName}/grader.cpp')
                flash('Uploaded!', 'success')
                awstools.problems.validateProblem(f'{problemName}')
                return redirect(f'/admin/editproblem/{problemName}')
            else:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'fileB_upload':
            # .h file for communication problems
            if 'fileB' not in files:
                flash('Header not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            if files['fileB'].filename == '':
                flash('Header not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            file_name = files['fileB'].filename
            if '.' not in file_name:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            ext_file = file_name.rsplit('.', 1)[1].lower()
            if ext_file == 'h':
                name = problemInfo['nameB']
                awstools.problems.uploadGrader(files['fileB'], f'{problemName}/{name}.h')
                flash('Uploaded!', 'success')
                awstools.problems.validateProblem(f'{problemName}')
                return redirect(f'/admin/editproblem/{problemName}')
            else:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'fileA_upload':
            # .h file for communication problems
            if 'fileA' not in files:
                flash('Header not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            if files['fileA'].filename == '':
                flash('Header not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            file_name = files['fileA'].filename
            if '.' not in file_name:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            ext_file = file_name.rsplit('.', 1)[1].lower()
            if ext_file == 'h':
                name = problemInfo['nameA']
                awstools.problems.uploadGrader(files['fileA'], f'{problemName}/{name}.h')
                flash('Uploaded!', 'success')
                awstools.problems.validateProblem(f'{problemName}')
                return redirect(f'/admin/editproblem/{problemName}')
            else:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] == 'header_upload':
            # Header upload for interactive or communication problems
            if 'header' not in files:
                flash('Header not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            if files['header'].filename == '':
                flash('Header not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            file_name = files['header'].filename
            if '.' not in file_name:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            ext_file = file_name.rsplit('.', 1)[1].lower()
            if ext_file == 'h':
                awstools.problems.uploadGrader(files['header'], f'{problemName}/{problemName}.h')
                flash('Uploaded!', 'success')
                awstools.problems.validateProblem(f'{problemName}')
                return redirect(f'/admin/editproblem/{problemName}')
            else:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            
        elif result['form_name'] == 'attachments_upload':
            if 'attachments' not in files:
                flash('Attachments not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            if files['attachments'].filename == '':
                flash('Attachments not found', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            file_name = files['attachments'].filename
            if '.' not in file_name:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')
            ext_file = file_name.rsplit('.', 1)[1].lower()
            if ext_file == 'zip':
                awstools.problems.uploadAttachments(files['attachments'], f'{problemName}.zip')
                flash('Uploaded!', 'success')
                awstools.problems.validateProblem(f'{problemName}')
                return redirect(f'/admin/editproblem/{problemName}')
            else:
                flash('Invalid file format', 'warning')
                return redirect(f'/admin/editproblem/{problemName}')

        elif result['form_name'] in ['regrade_problem', 'regrade_nonzero', 'regrade_acs']:
            # REGRADE PROBLEM

            # Regrade type can be NORMAL, AC, NONZERO
            regradeType = 'NORMAL'
            if result['form_name'] == 'regrade_nonzero': regradeType = 'NONZERO'
            if result['form_name'] == 'regrade_acs': regradeType = 'AC'

            if userInfo['role'] == 'admin':
                awstools.problems.regradeProblem(problemName=problemName, regradeType=regradeType)
                flash('Regrade request sent to server!', 'success')
            else: 
                flash('You need admin access to do this', 'warning')
            return redirect(f'/admin/editproblem/{problemName}')

        else:
            flash ("An error has occured", "warning")
            return redirect(f'/admin/editproblem/{problemName}')

    return render_template('editproblem.html', form=form, info=problemInfo, userinfo=userInfo)
