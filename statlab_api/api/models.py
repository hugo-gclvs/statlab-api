from django.db import models


class Absence(models.Model):
    subject = models.CharField(max_length=100)
    subjectType = models.CharField(max_length=100)
    classroom = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    justification = models.CharField(max_length=100)
    username = models.CharField(max_length=100)

    def to_dict(self):
        return {
            'subject': self.subject,
            'subjectType': self.subjectType,
            'classroom': self.classroom,
            'teacher': self.teacher,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'justification': self.justification,
            'username': self.username,
        }

class User(models.Model):
    username = models.CharField(max_length=100)

    def to_dict(self):
        return {
            'username': self.username
        }