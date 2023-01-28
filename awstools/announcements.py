import os
import json
import boto3
from uuid import uuid4
from datetime import datetime

from awstools import awshelper
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
judgeName = os.environ.get('JUDGE_NAME')
announcements_table = dynamodb.Table(f'{judgeName}-announcements')

# Gets all announcements for homepage
def getAllAnnouncements():
	return awshelper.scan(announcements_table)

def createAnnouncement(title, text):
	info = {}
	info['announcementId'] = str(uuid4())
	info['title'] = title
	info['text'] = text
	info['announcementTime'] = str(datetime.utcnow().strftime("%Y-%m-%d %X"))

	# Trigger AWS Lambda function to activate announcement notification

	announcements_table.put_item(Item=info)