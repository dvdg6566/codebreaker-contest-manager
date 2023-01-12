from flask import render_template, session, redirect, request, flash
import awstools

def announcelist():
    userInfo=awstools.users.getCurrentUserInfo()
    announceInf=awstools.announcements.getAllAnnounces()
    announceInfl = []
    for info in announceInf:
        if not info['visible']:
            continue
        if info['adminOnly'] and (userInfo != None and (userInfo['role'] == 'admin' or userInfo['role'] == 'superadmin')):
            announceInfl.append((info['priority'], info))
        if not info['adminOnly']:
            announceInfl.append((info['priority'], info))
    announceInfl.sort()
    announceInfl.reverse()
    announceInfo = []
    announcenames = []
    for info in announceInfl:
        announceInfo.append(info[1])
        announcenames.append(info[1]['announceId'])

    return render_template('announcelist.html', userinfo=userInfo, announceinfo=announceInfo)
