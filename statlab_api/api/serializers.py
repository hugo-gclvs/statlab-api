from .utils.firestore_utils import convert_document_to_dict, db
from rest_framework import serializers
from api.models import Absence, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from services.session_manager import SessionManager
from services.oge_scraper import OgeScraper
from services.absence_service import AbsenceService
from services.personal_info_service import PersonalInfoService
from google.cloud.firestore_v1.base_query import FieldFilter
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
import asyncio

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'specialization', 'study_year')

class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absence
        fields = ('id', 'subject', 'subjectType', 'classroom', 'teacher', 'start_date', 'end_date', 'justification', 'username')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = RefreshToken()
        token['user_id'] = user['id']
        return token

    def validate(self, attrs):
        username, password = self.get_credentials(attrs)
        session_manager = SessionManager(user=username, pwd=password)
        if not session_manager.login():
            raise AuthenticationFailed('No active account found with the given credentials')

        user = self.get_or_create_user(username, session_manager)
        self.process_user_absences(username, session_manager)

        return self.get_token_response(user)

    def get_credentials(self, attrs):
        return attrs.get('username'), attrs.get('password')

    def validate_user_credentials(self, username, password):
        if not SessionManager(user=username, pwd=password).login():
            raise AuthenticationFailed('No active account found with the given credentials')

    def get_or_create_user(self, username, session_manager):
        user_query = db.collection('users').where(filter=FieldFilter('username', '==', username)).get()
        oge_scraper = OgeScraper(session_manager)
        personal_info_service = PersonalInfoService(oge_scraper)

        if not user_query:
            user_ref = db.collection('users').document()
            user = personal_info_service.getStudentInfo()
            user_ref.set({
                "username": username,
                "last_name": user['last_name'],
                "first_name": user['first_name'],
                "specialization": user['specialization'],
                "study_year": user['study_year'],
            })
            user_query = db.collection('users').where(filter=FieldFilter('username', '==', username)).get()

        return convert_document_to_dict(user_query[0])

    async def process_user_absences(self, username, session_manager):
        absences = await asyncio.to_thread(self.scrape_user_absences(username, session_manager))
        await asyncio.to_thread(self.store_absences_in_firestore(absences, username))

    async def scrape_user_absences(self, username, session_manager):
        oge_scraper = OgeScraper(session_manager)
        return AbsenceService(oge_scraper).getAllAbsences()

    async def store_absences_in_firestore(self, absences, username):
        user_ref = self.get_user_reference(username)
        batch = db.batch() 

        for absence in self.prepare_absences(absences, user_ref):
            if not self.absence_exists(absence, user_ref):
                doc_ref = db.collection('absences').document()
                batch.set(doc_ref, absence)

        batch.commit() 

    def get_user_reference(self, username):
        return db.collection('users').where(filter=FieldFilter('username', '==', username)).get()[0].reference

    def prepare_absences(self, absences, user_ref):
        subject_type_mapping = {
            'CM': '/subject_type/CM', 'TD': '/subject_type/TD',
            'TP': '/subject_type/TP', 'Projet': '/subject_type/Projet'
        }

        for absence in absences:
            absence_dict = absence.to_dict() if hasattr(absence, 'to_dict') else absence
            absence_dict.pop('id', None)
            absence_dict['username'] = user_ref
            absence_dict['subjectType'] = subject_type_mapping.get(absence_dict.get('subjectType'), absence_dict.get('subjectType'))
            yield absence_dict

    def absence_exists(self, absence, user_ref):
        start_date, end_date = absence['start_date'], absence['end_date']
        existing_absences = db.collection('absences').where(filter=FieldFilter('username', '==', user_ref)) \
            .where(filter=FieldFilter('start_date', '==', start_date)).where(filter=FieldFilter('end_date', '==', end_date)).get()
        return bool(existing_absences)

    def get_token_response(self, user):
        refresh = self.get_token(user)
        return {
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': user
        }
