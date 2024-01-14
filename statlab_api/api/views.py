import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils.firestore_utils import get_top_users_with_most_absences_by_classroom_from_firestore, get_top_users_with_most_absences_by_justification_from_firestore, get_top_users_with_most_absences_by_subject_from_firestore, get_top_users_with_most_absences_by_subject_type_from_firestore, get_top_users_with_most_absences_by_teacher_from_firestore, get_top_users_with_most_absences_from_firestore, get_user_absences, get_filtered_user_absences
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


logger = logging.getLogger(__name__)

token_param = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Bearer token",
    type=openapi.TYPE_STRING,
    bearerFormat="JWT",
    required=True
)

class BaseAuthenticatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_id_from_token(self, request):
        raw_token = request.headers.get('Authorization').split()[1]
        validated_token = JWTAuthentication().get_validated_token(raw_token)
        return validated_token.get('user_id')

class LoginView(APIView):

    @swagger_auto_schema(
        operation_description="Authenticates a user and returns a JWT token and the user's information",
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: openapi.Response(
                description="Authentication successful",
                examples={
                    'application/json': {
                        'tokens': {
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX...',
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2Vy...',
                        },
                        'user': {
                            'username': 'username',
                            'first_name': 'first_name',
                            'last_name': 'last_name',
                            'specialization': 'specialization',
                            'study_year': 'study_year'
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Authentication failed",
                examples={
                    'application/json': {
                        'non_field_errors': [
                            "Unable to log in with provided credentials."
                        ]
                    }
                }
            )
        }
    )

    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAbsencesView(BaseAuthenticatedView):

    @swagger_auto_schema(
        operation_description="Returns the absences of the user",
        manual_parameters=[
            token_param,
        ],
        responses={
            200: openapi.Response(
                description="Absences retrieved successfully",
                examples={
                    'application/json': {
                        'absences': [
                            {
                                'id': 'absence_id',
                                'date': '2021-01-01',
                                'teacher': 'teacher_name',
                                'classroom': 'classroom_name',
                                'subjectType': 'subject_type',
                                'subject': 'subject_name',
                                'justification': 'justification',
                                'username': 'username',
                                'start_date': '2023-09-19T10:15:00+00:00',
                                'end_date': '2023-09-19T11:15:00+00:00',
                            }
                        ]
                    }
                }
            ),
            500: openapi.Response(
                description="An error occurred while retrieving absences",
                examples={
                    'application/json': {
                        'error': 'Error message'
                    }
                }
            )
        }
    )

    def get(self, request, *args, **kwargs):
        try:
            user_id = self.get_user_id_from_token(request)
            absences = get_user_absences(user_id)
            return Response({"absences": absences})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilteredAbsencesView(BaseAuthenticatedView):

    @swagger_auto_schema(
        operation_description="Returns the filtered absences of the user. All parameters are optional and can be combined.",
        manual_parameters=[
            token_param,
            openapi.Parameter('teacher', openapi.IN_QUERY, description="Nom de l'enseignant", type=openapi.TYPE_STRING),
            openapi.Parameter('classroom', openapi.IN_QUERY, description="Nom de la classe", type=openapi.TYPE_STRING),
            openapi.Parameter('subjectType', openapi.IN_QUERY, description="Type de matière", type=openapi.TYPE_STRING),
            openapi.Parameter('subject', openapi.IN_QUERY, description="Nom de la matière", type=openapi.TYPE_STRING),
            openapi.Parameter('justification', openapi.IN_QUERY, description="Justification", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Absences retrieved successfully",
                examples={
                    'application/json': {
                        'absences': [
                            {
                                'id': 'absence_id',
                                'date': '2021-01-01',
                                'teacher': 'teacher_name',
                                'classroom': 'classroom_name',
                                'subjectType': 'subject_type',
                                'subject': 'subject_name',
                                'justification': 'justification',
                                'username': 'username',
                                'start_date': '2023-09-19T10:15:00+00:00',
                                'end_date': '2023-09-19T11:15:00+00:00',
                            }
                        ]
                    }
                }
            ),
            500: openapi.Response(
                description="An error occurred while retrieving absences",
                examples={
                    'application/json': {
                        'error': 'Error message'
                    }
                }
            )
        }
    )

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

    @swagger_auto_schema(
        operation_description="Returns the top n users with the most absences. \"Type\" is not optional and must be one of the following: global, teacher, classroom, subject, subject_type, justification. Other parameters depend on the type. You can't combined type. Note that the top_n parameter is optional and defaults to 10.",
        manual_parameters=[
            token_param,
            openapi.Parameter('type', openapi.IN_QUERY, description="Statistiques type", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('top_n', openapi.IN_QUERY, description="Results count", type=openapi.TYPE_INTEGER),
            openapi.Parameter('teacher', openapi.IN_QUERY, description="Teacher name", type=openapi.TYPE_STRING),
            openapi.Parameter('classroom', openapi.IN_QUERY, description="Classroom name", type=openapi.TYPE_STRING),
            openapi.Parameter('subject', openapi.IN_QUERY, description="Subject name", type=openapi.TYPE_STRING),
            openapi.Parameter('subject_type', openapi.IN_QUERY, description="Subject type", type=openapi.TYPE_STRING),
            openapi.Parameter('justification', openapi.IN_QUERY, description="Justification", type=openapi.TYPE_BOOLEAN),
        ],
        responses={
            200: openapi.Response(
                description="Statistics retrieved successfully",
                examples={
                    'application/json': {
                        'top_n_global_ranking': [
                            {
                                'username': 'username',
                                'first_name': 'first_name',
                                'last_name': 'last_name',
                                'specialization': 'specialization',
                                'study_year': 'study_year'
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid type",
                examples={
                    'application/json': {
                        'error': 'Invalid type'
                    }
                }
            ),
            500: openapi.Response(
                description="An error occurred while retrieving statistics",
                examples={
                    'application/json': {
                        'error': 'Error message'
                    }
                }
            )
        }
    )

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
        return Response({"top_"+str(top_n)+"_global_ranking": ranking})
    
    def get_top_users_with_most_absences_by_teacher(self, params, top_n):
        teacher_name = params.get('teacher')
        ranking = get_top_users_with_most_absences_by_teacher_from_firestore(teacher_name, top_n)
        return Response({"top_"+str(top_n)+"_teacher_ranking": ranking})
    
    def get_top_users_with_most_absences_by_classroom(self, params, top_n):
        classroom = params.get('classroom')
        ranking = get_top_users_with_most_absences_by_classroom_from_firestore(classroom, top_n)
        return Response({"top_"+str(top_n)+"_classroom_ranking": ranking})
    
    def get_top_users_with_most_absences_by_subject(self, params, top_n):
        subject = params.get('subject')
        ranking = get_top_users_with_most_absences_by_subject_from_firestore(subject, top_n)
        return Response({"top_"+str(top_n)+"_subject_ranking": ranking})
    
    def get_top_users_with_most_absences_by_subject_type(self, params, top_n):
        subject_type = params.get('subject_type')
        ranking = get_top_users_with_most_absences_by_subject_type_from_firestore(subject_type, top_n)
        return Response({"top_"+str(top_n)+"_subject_type_ranking": ranking})
    
    def get_top_users_with_most_absences_by_justification(self, params, top_n):
        justification = params.get('areJustified', 'false')
        ranking = get_top_users_with_most_absences_by_justification_from_firestore(justification, top_n)
        ranking_key = f"top_{top_n}_{'justified' if justification == 'true' else 'unjustified'}_ranking"
        return Response({ranking_key: ranking})