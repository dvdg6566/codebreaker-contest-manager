from flask import render_template, session, redirect, request, flash, url_for
from forms import newAnnouncementForm

import os
import awstools
from datetime import datetime, timedelta

# Gets timezone from environment variables
TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET'))

def announcements():
	userInfo=awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect(url_for("login", next=request.url))

	# ACCESS CONTROL
	if userInfo['role'] == 'member': 
		contestInfo = awstools.contests.getContestInfo(userInfo['contest'])
		if contestInfo == None or contestInfo['status'] != 'ONGOING':
			flash("This resource is only accessible during contests!", "warning")
			return redirect('/')

	announcementsInfo = awstools.announcements.getAllAnnouncements()
	for announcement in announcementsInfo:
		timestamp = datetime.strptime(announcement['announcementTime'], "%Y-%m-%d %X")
		timestamp += timedelta(hours=TIMEZONE_OFFSET) # Account for timezone
		announcement['announcementTime'] = timestamp
		
	announcementsInfo.sort(key = lambda x:x['announcementTime']) # Sort announcements by time
	announcementsInfo.reverse() # Latest time first
	for announcement in announcementsInfo:
		announcement['announcementTime'] = datetime.strftime(announcement['announcementTime'], "%Y-%m-%d %X")

	form=newAnnouncementForm()

	if form.is_submitted():
		if userInfo['role'] != 'admin':
			flash("Admin access is required", "danger")
			return redirect("/announcements")

		result = request.form

		title = result.get('announcement_title')
		text = result.get('announcement_text')
		
		awstools.announcements.createAnnouncement(title=title, text=text)

		flash("Announcement Posted!", "success")

		return redirect(f'/announcements')

	return render_template('announcelist.html', form=form, userinfo=userInfo, announcementsInfo=announcementsInfo)

