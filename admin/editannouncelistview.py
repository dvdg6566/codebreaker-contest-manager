import os
from flask import render_template, session, redirect, request, flash
from datetime import datetime, timedelta
import awstools
from forms import newAnnouncementForm

# Gets timezone from environment variables

TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET'))

def editannouncelist():
	userInfo=awstools.users.getCurrentUserInfo()
	if userInfo == None: return redirect(url_for("login", next=request.url))
	if userInfo['role'] != 'admin':
		flash("Admin access is required", "warning")
		return redirect("/")

	announcementsInfo = awstools.announcements.getAllAnnouncements()
	for announcement in announcementsInfo:
		timestamp = datetime.strptime(announcement['announcementTime'], "%Y-%m-%d %X")
		timestamp += timedelta(hours=TIMEZONE_OFFSET)
		announcement['announcementTime'] = datetime.strftime(timestamp, "%Y-%m-%d %X")
		print(timestamp)

	form=newAnnouncementForm()

	if form.is_submitted():
		result = request.form

		title = result.get('announcement_title')
		text = result.get('announcement_text')
		
		awstools.announcements.createAnnouncement(title=title, text=text)

		flash("Announcement Posted", "success")

		return redirect(f'/admin/editannouncements')

	return render_template('editannouncelist.html', form=form, userinfo=userInfo, announcementsInfo=announcementsInfo)

