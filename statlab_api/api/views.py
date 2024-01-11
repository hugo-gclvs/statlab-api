from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CustomTokenObtainPairSerializer
from firebase_admin import firestore
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils.firestore_utils import db, convert_document_to_dict


db = firestore.client()

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

        absences = self.get_user_absences(user_id)
        return Response({"absences": absences})

    def get_user_absences(self, user_id):
        user_ref = db.collection('users').document(user_id)
        absences_query = db.collection('absences').where('username', '==', user_ref).get()

        print(absences_query)

        # Convert the documents returned by the query into a dictionary
        absences = [convert_document_to_dict(absence) for absence in absences_query]
        return absences
    

class FilteredAbsencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        raw_token = request.headers.get('Authorization').split()[1]
        validated_token = JWTAuthentication().get_validated_token(raw_token)
        user_id = validated_token.get('user_id')
        
        teacher_name = request.query_params.get('teacher')
        classroom = request.query_params.get('classroom')

        absences = self.get_filtered_absences(user_id, teacher_name, classroom)
        return Response({"absences": absences})

    def get_filtered_absences(self, user_id, teacher_name, classroom):
        user_ref = db.collection('users').document(user_id)
        query = db.collection('absences').where('username', '==', user_ref)

        if teacher_name:
            query = query.where('teacher', '==', teacher_name)
        if classroom:
            query = query.where('classroom', '==', classroom)

        absences_query = query.get()
        absences = [convert_document_to_dict(absence) for absence in absences_query]
        return absences

