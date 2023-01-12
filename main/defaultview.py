from flask import redirect

def default():
    if contestmode.contest():
        return redirect(f'/contest/{contestmode.contestId()}')
    return redirect('/')
