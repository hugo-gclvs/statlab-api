from django.db import models
from datetime import datetime

class Absence():

	def __init__(self, id, subject, subjectType, classroom, teacher, start_date, end_date, justification):
		self.id = id
		self.subject = subject
		self.subjectType = subjectType
		self.classroom = classroom
		self.teacher = teacher
		self.start_date = datetime.fromtimestamp(start_date)
		self.end_date = datetime.fromtimestamp(end_date)
		self.justification = justification

	def __str__(self):
		return self.id + " " + self.subject + " - " + self.subjectType + " - " + self.classroom + " - " + self.teacher + " - " + str(self.start_date) + " - " + str(self.end_date) + " - " + self.justification

	def to_dict(self):
		return {
			'id': self.id,
			'subject': self.subject,
			'subjectType': self.subjectType,
			'teacher': self.teacher,
			'classroom': self.classroom,
			'start_date': self.start_date,
			'end_date': self.end_date,
			'justification': self.justification
		}
		
