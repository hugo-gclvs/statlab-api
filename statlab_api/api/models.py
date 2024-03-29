from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    specialization = models.CharField(max_length=100, null=True)
    study_year = models.CharField(max_length=100, null=True)

    def to_dict(self):
        return {
            'username': self.username,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'specialization': self.specialization,
            'study_year': self.study_year,
        }

class Absence(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
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
            'id': self.id,
            'subject': self.subject,
            'subjectType': self.subjectType,
            'classroom': self.classroom,
            'teacher': self.teacher,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'justification': self.justification,
            'username': self.username,
        }

