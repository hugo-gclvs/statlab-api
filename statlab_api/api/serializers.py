from .utils.firestore_utils import convert_document_to_dict, db
from rest_framework import serializers
from api.models import Absence, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from services.session_manager import SessionManager
from services.oge_scraper import OgeScraper
from services.absence_service import AbsenceService

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

    def create(self, validated_data):
        # Logique pour créer un utilisateur dans Firestore
        # Retournez le dictionnaire de l'utilisateur créé
        pass

    def update(self, instance, validated_data):
        # Logique pour mettre à jour un utilisateur dans Firestore
        # Retournez le dictionnaire de l'utilisateur mis à jour
        pass

class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absence
        fields = ('id', 'subject', 'subjectType', 'classroom', 'teacher', 'start_date', 'end_date', 'justification', 'username')


    def create(self, validated_data):
        # Logique pour créer une absence dans Firestore


        # Retournez le dictionnaire de l'absence créée
        pass

    def update(self, instance, validated_data):
        # Logique pour mettre à jour une absence dans Firestore


        # Retournez le dictionnaire de l'absence mise à jour
        pass


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = RefreshToken()
        print(user['id'])
        token['user_id'] = user['id']
        return token

    def validate(self, attrs):
        username, password = self.get_credentials(attrs)
        self.validate_user_credentials(username, password)

        user = self.get_or_create_user(username)
        self.process_user_absences(username, password)

        return self.get_token_response(user)

    def get_credentials(self, attrs):
        return attrs.get('username'), attrs.get('password')

    def validate_user_credentials(self, username, password):
        if not SessionManager(user=username, pwd=password).login():
            raise AuthenticationFailed('No active account found with the given credentials')

    def get_or_create_user(self, username):
        user_query = db.collection('users').where('username', '==', username).get()
        if not user_query:
            user_ref = db.collection('users').document()
            user_ref.set({"username": username})
            return {"username": username, "reference": user_ref}
        return convert_document_to_dict(user_query[0])

    def process_user_absences(self, username, password):
        absences = self.scrape_user_absences(username, password)
        self.store_absences_in_firestore(absences, username)

    def scrape_user_absences(self, username, password):
        session_manager = SessionManager(user=username, pwd=password)
        session_manager.login()
        oge_scraper = OgeScraper(session_manager)
        return AbsenceService(oge_scraper).getAllAbsences()

    def store_absences_in_firestore(self, absences, username):
        user_ref = self.get_user_reference(username)
        for absence in self.prepare_absences(absences, user_ref):
            if not self.absence_exists(absence, user_ref):
                db.collection('absences').document().set(absence)

    def get_user_reference(self, username):
        return db.collection('users').where('username', '==', username).get()[0].reference

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
        existing_absences = db.collection('absences').where('username', '==', user_ref) \
            .where('start_date', '==', start_date).where('end_date', '==', end_date).get()
        return bool(existing_absences)

    def get_token_response(self, user):
        refresh = self.get_token(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}
