from django.contrib.auth.models import Group, User
from rest_framework import serializers
from api.models import Absence
from datetime import datetime


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class AbsenceSerializer(serializers.Serializer):
    class Meta:
        model = Absence
        fields = ['id', 'subject', 'subjectType', 'classroom', 'teacher', 'start_date', 'end_date', 'justification']

    id = serializers.CharField(max_length=200)
    subject = serializers.CharField(max_length=200)
    subjectType = serializers.CharField(max_length=200)
    classroom = serializers.CharField(max_length=200)
    teacher = serializers.CharField(max_length=200)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    justification = serializers.CharField(max_length=200)

    def create(self, validated_data):
        return Absence(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.subjectType = validated_data.get('subjectType', instance.subjectType)
        instance.classroom = validated_data.get('classroom', instance.classroom)
        instance.teacher = validated_data.get('teacher', instance.teacher)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.justification = validated_data.get('justification', instance.justification)
        return instance