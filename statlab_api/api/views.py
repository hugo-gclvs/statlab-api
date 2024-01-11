from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CustomTokenObtainPairSerializer
from firebase_admin import firestore
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils.firestore_utils import db, convert_document_to_dict

# Initialize Firestore client
db = firestore.client()

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Authenticate user and return a JWT token if valid credentials are provided.
        """
        serializer = CustomTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAbsencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve absences for the authenticated user.
        """
        try:
            raw_token = request.headers.get('Authorization').split()[1]
            validated_token = JWTAuthentication().get_validated_token(raw_token)
            user_id = validated_token.get('user_id')

            absences = self.get_user_absences(user_id)
            return Response({"absences": absences})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_user_absences(self, user_id):
        """
        Get absences for a user from Firestore.
        """
        user_ref = db.collection('users').document(user_id)
        absences_query = db.collection('absences').where('username', '==', user_ref).get()
        absences = [convert_document_to_dict(absence) for absence in absences_query]
        return absences

class FilteredAbsencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve filtered absences for the authenticated user based on query parameters.
        """
        try:
            raw_token = request.headers.get('Authorization').split()[1]
            validated_token = JWTAuthentication().get_validated_token(raw_token)
            user_id = validated_token.get('user_id')

            teacher_name = request.query_params.get('teacher')
            classroom = request.query_params.get('classroom')

            absences = self.get_filtered_absences(user_id, teacher_name, classroom)
            return Response({"absences": absences})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_filtered_absences(self, user_id, teacher_name, classroom):
        """
        Get filtered absences for a user from Firestore based on query parameters.
        """
        user_ref = db.collection('users').document(user_id)
        query = db.collection('absences').where('username', '==', user_ref)

        if teacher_name:
            query = query.where('teacher', '==', teacher_name)
        if classroom:
            query = query.where('classroom', '==', classroom)

        absences_query = query.get()
        absences = [convert_document_to_dict(absence) for absence in absences_query]
        return absences
