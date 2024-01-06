import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Absence, User
from .serializers import AbsenceSerializer, UserSerializer
from firebase_admin import firestore
from django.http import JsonResponse
from .utils.firestore_utils import db, convert_document_to_dict, retrieve_absence_by_id, retrieve_absences, get_user_details

db = firestore.client()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request):
        users = db.collection('users').get()
        return Response([convert_document_to_dict(user) for user in users])

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Use the create() method of the serializer
            return Response(user)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        existing_user = get_user_details(pk)
        serializer = UserSerializer(existing_user, data=request.data)
        if serializer.is_valid():
            updated_user = serializer.save()  # Use the update() method of the serializer
            return Response(updated_user)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def absences(self, request, pk=None):
        absences = retrieve_absences_by_user(pk)  # Retrieve absences from Firestore
        serializer = AbsenceSerializer(absences, many=True)  # Serialize the data
        return Response(serializer.data)

def retrieve_absences_by_user(username):
    try:
        absences_ref = db.collection('absences').where('username', '==', username)
        absences = absences_ref.get()
        return [convert_document_to_dict(absence) for absence in absences]
    except Exception as e:
        # Handle any errors
        pass

class AbsenceViewSet(viewsets.ModelViewSet):
    serializer_class = AbsenceSerializer
    queryset = Absence.objects.all()

    def list(self, request):
        absences = retrieve_absences()  # Retrieve absences from Firestore
        serializer = AbsenceSerializer(absences, many=True)  # Serialize the data
        return Response(serializer.data) 

    def create(self, request):
        serializer = AbsenceSerializer(data=request.data)
        if serializer.is_valid():
            absence = serializer.save()  # Use the create() method of the serializer
            return Response(absence)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        existing_absence = retrieve_absence_by_id(pk)
        serializer = AbsenceSerializer(existing_absence, data=request.data)
        if serializer.is_valid():
            updated_absence = serializer.save()  # Use the update() method of the serializer
            return Response(updated_absence)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        # Logic to delete an absence from Firestore
        return Response({'message': 'Absence successfully deleted!'})
