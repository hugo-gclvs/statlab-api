import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils.firestore_utils import get_top_users_with_most_absences_by_classroom_from_firestore, get_top_users_with_most_absences_by_justification_from_firestore, get_top_users_with_most_absences_by_subject_from_firestore, get_top_users_with_most_absences_by_subject_type_from_firestore, get_top_users_with_most_absences_by_teacher_from_firestore, get_top_users_with_most_absences_from_firestore, get_user_absences, get_filtered_user_absences


logger = logging.getLogger(__name__)

class BaseAuthenticatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_id_from_token(self, request):
        raw_token = request.headers.get('Authorization').split()[1]
        validated_token = JWTAuthentication().get_validated_token(raw_token)
        return validated_token.get('user_id')

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAbsencesView(BaseAuthenticatedView):
    def get(self, request, *args, **kwargs):
        try:
            user_id = self.get_user_id_from_token(request)
            absences = get_user_absences(user_id)
            return Response({"absences": absences})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilteredAbsencesView(BaseAuthenticatedView):
    def get(self, request, *args, **kwargs):
        try:
            user_id = self.get_user_id_from_token(request)
            teacher_name = request.query_params.get('teacher')
            classroom = request.query_params.get('classroom')
            subjectType = request.query_params.get('subjectType')
            subject = request.query_params.get('subject')
            justification = request.query_params.get('justification')

            absences = get_filtered_user_absences(user_id, teacher_name, classroom, subjectType, subject, justification)
            return Response({"absences": absences})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AbsenceStatistiquesView(BaseAuthenticatedView):
    STATISTICS_MAPPING = {
        'global': 'get_top_users_with_most_absences',
        'teacher': 'get_top_users_with_most_absences_by_teacher',
        'classroom': 'get_top_users_with_most_absences_by_classroom',
        'subject': 'get_top_users_with_most_absences_by_subject',
        'subject_type': 'get_top_users_with_most_absences_by_subject_type',
        'justification': 'get_top_users_with_most_absences_by_justification'
    }

    def get(self, request, *args, **kwargs):
        try:
            user_id = self.get_user_id_from_token(request)
            stat_type = request.query_params.get('type')
            method_name = self.STATISTICS_MAPPING.get(stat_type)
            top_n = self.get_top_n_param(request)

            if not method_name:
                return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

            return getattr(self, method_name)(request.query_params, top_n)

        except Exception as e:
            return self.handle_error(e)
        
    def handle_error(self, exception):
        logger.error(f"Error in AbsenceStatisticsView: {exception}")
        return Response({"error": str(exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_top_n_param(self, request):
        top_n = request.query_params.get('top_n', 10)
        try:
            top_n = int(top_n)
            if top_n <= 0:
                raise ValueError("top_n must be a positive integer")
            if top_n > 50:
                raise ValueError("top_n must be less than or equal to 50")
            return top_n
        except ValueError:
            return self.handle_error(ValueError("top_n is not valid"))

        
    def get_top_users_with_most_absences(self, params, top_n):
        ranking = get_top_users_with_most_absences_from_firestore(top_n)
        return Response({"top_10_global_ranking": ranking})
    
    def get_top_users_with_most_absences_by_teacher(self, params, top_n):
        teacher_name = params.get('teacher')
        ranking = get_top_users_with_most_absences_by_teacher_from_firestore(teacher_name, top_n)
        return Response({"top_10_teacher_ranking": ranking})
    
    def get_top_users_with_most_absences_by_classroom(self, params, top_n):
        classroom = params.get('classroom')
        ranking = get_top_users_with_most_absences_by_classroom_from_firestore(classroom, top_n)
        return Response({"top_10_classroom_ranking": ranking})
    
    def get_top_users_with_most_absences_by_subject(self, params, top_n):
        subject = params.get('subject')
        ranking = get_top_users_with_most_absences_by_subject_from_firestore(subject, top_n)
        return Response({"top_10_subject_ranking": ranking})
    
    def get_top_users_with_most_absences_by_subject_type(self, params, top_n):
        subject_type = params.get('subject_type')
        ranking = get_top_users_with_most_absences_by_subject_type_from_firestore(subject_type, top_n)
        return Response({"top_10_subject_type_ranking": ranking})
    
    def get_top_users_with_most_absences_by_justification(self, params, top_n):
        justification = params.get('areJustified', 'false')
        ranking = get_top_users_with_most_absences_by_justification_from_firestore(justification, top_n)
        ranking_key = f"top_10_{'justified' if justification == 'true' else 'unjustified'}_ranking"
        return Response({ranking_key: ranking})