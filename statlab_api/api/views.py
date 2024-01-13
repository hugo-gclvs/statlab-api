from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils.firestore_utils import get_top_10_users_with_most_absences_by_classroom_from_firestore, get_top_10_users_with_most_absences_by_justification_from_firestore, get_top_10_users_with_most_absences_by_subject_from_firestore, get_top_10_users_with_most_absences_by_subject_type_from_firestore, get_top_10_users_with_most_absences_by_teacher_from_firestore, get_top_10_users_with_most_absences_from_firestore, get_user_absences, get_filtered_user_absences


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
    def get(self, request, *args, **kwargs):
        try:
            user_id = self.get_user_id_from_token(request)
            
            statistique_type = request.query_params.get('type')
            teacher = request.query_params.get('teacher')
            classroom = request.query_params.get('classroom')
            subject = request.query_params.get('subject')
            subject_type = request.query_params.get('subject_type')
            justification = request.query_params.get('areJustified')

            if statistique_type == 'global':
                return self.get_top_10_users_with_most_absences()
            elif statistique_type == 'teacher':
                return self.get_top_10_users_with_most_absences_by_teacher(teacher)
            elif statistique_type == 'classroom':
                return self.get_top_10_users_with_most_absences_by_classroom(classroom)
            elif statistique_type == 'subject':
                return self.get_top_10_users_with_most_absences_by_subject(subject)
            elif statistique_type == 'subject_type':
                return self.get_top_10_users_with_most_absences_by_subject_type(subject_type)
            elif statistique_type == 'justification':
                return self.get_top_10_users_with_most_absences_by_justification(justification)
            else:
                return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_top_10_users_with_most_absences(self):
        ranking = get_top_10_users_with_most_absences_from_firestore()
        return Response({"top_10_global_ranking": ranking})
    
    def get_top_10_users_with_most_absences_by_teacher(self, teacher_name):
        ranking = get_top_10_users_with_most_absences_by_teacher_from_firestore(teacher_name)
        return Response({"top_10_teacher_ranking": ranking})
    
    def get_top_10_users_with_most_absences_by_classroom(self, classroom):
        ranking = get_top_10_users_with_most_absences_by_classroom_from_firestore(classroom)
        return Response({"top_10_classroom_ranking": ranking})
    
    def get_top_10_users_with_most_absences_by_subject(self, subject):
        ranking = get_top_10_users_with_most_absences_by_subject_from_firestore(subject)
        return Response({"top_10_subject_ranking": ranking})
    
    def get_top_10_users_with_most_absences_by_subject_type(self, subject_type):
        ranking = get_top_10_users_with_most_absences_by_subject_type_from_firestore(subject_type)
        return Response({"top_10_subject_type_ranking": ranking})
    
    def get_top_10_users_with_most_absences_by_justification(self, justification):
        ranking = get_top_10_users_with_most_absences_by_justification_from_firestore(justification)
        if justification == 'true':
            return Response({"top_10_justified_ranking": ranking})
        else:
            return Response({"top_10_unjustified_ranking": ranking})