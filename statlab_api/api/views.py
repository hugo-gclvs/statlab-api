import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Absence, User
from .serializers import AbsenceSerializer, UserSerializer, CustomTokenObtainPairSerializer
from firebase_admin import firestore
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils.firestore_utils import db, convert_document_to_dict, retrieve_absence_by_id, retrieve_absences, get_user_details, retrieve_absences_by_user


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

# class AbsenceViewSet(viewsets.ModelViewSet):
#     serializer_class = AbsenceSerializer
#     queryset = Absence.objects.all()

#     def list(self, request):
#         absences = retrieve_absences()  # Retrieve absences from Firestore
#         serializer = AbsenceSerializer(absences, many=True)  # Serialize the data
#         return Response(serializer.data) 

#     def create(self, request):
#         serializer = AbsenceSerializer(data=request.data)
#         if serializer.is_valid():
#             absence = serializer.save()  # Use the create() method of the serializer
#             return Response(absence)
#         return Response(serializer.errors, status=400)

#     def update(self, request, pk=None):
#         existing_absence = retrieve_absence_by_id(pk)
#         serializer = AbsenceSerializer(existing_absence, data=request.data)
#         if serializer.is_valid():
#             updated_absence = serializer.save()  # Use the update() method of the serializer
#             return Response(updated_absence)
#         return Response(serializer.errors, status=400)

#     def destroy(self, request, pk=None):
#         # Logic to delete an absence from Firestore
#         return Response({'message': 'Absence successfully deleted!'})

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

class UserAbsencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get JWT from Authorization header
        raw_token = request.headers.get('Authorization').split()[1]
        validated_token = JWTAuthentication().get_validated_token(raw_token)
        user_id = validated_token.get('user_id')

        print(user_id)
        absences = self.get_user_absences(user_id)
        return Response({"absences": absences})

    def get_user_absences(self, user_id):
        user_ref = db.collection('users').document(user_id)
        absences_query = db.collection('absences').where('username', '==', user_ref).get()

        print(absences_query)

        # Convert the documents returned by the query into a dictionary
        absences = [convert_document_to_dict(absence) for absence in absences_query]
        return absences

