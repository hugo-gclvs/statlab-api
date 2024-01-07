import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from .models import Absence, User
from .serializers import AbsenceSerializer, UserSerializer
from firebase_admin import firestore
from django.http import JsonResponse
from .utils.firestore_utils import db, convert_document_to_dict, retrieve_absence_by_id, retrieve_absences, get_user_details, retrieve_absences_by_user
from services.session_manager import SessionManager

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

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Both username and password are required."}, status=status.HTTP_400_BAD_REQUEST)



        if user_is_valid(username, password): 
            # check if user exists in firestore
            user = db.collection('users').where('username', '==', username).get()
            if len(user) > 0:
                return Response({"message": "Login successful"})
            # if not, create a new user
            user_ref = db.collection('users').document()
            user_ref.set({"username": username})
            
            return Response({"message": "Login successful"})
        else:
            return Response({"error": "Invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        

def user_is_valid(username, password):
    session_manager = SessionManager(user=username, pwd=password)

    if session_manager.login():
        return True
    else:
        return False