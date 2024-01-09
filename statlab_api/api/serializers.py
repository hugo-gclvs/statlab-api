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
        token['username'] = user['username']
        return token

    def validate(self, attrs):
        username, password = attrs.get('username'), attrs.get('password')

        if not self.user_is_valid(username, password):
            raise AuthenticationFailed('No active account found with the given credentials')

        user = self.get_or_create_user(username)
        self.scrape_and_store_user_absences(username, password)

        refresh = self.get_token(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}

    def user_is_valid(self, username, password):
        return SessionManager(user=username, pwd=password).login()

    def get_or_create_user(self, username):
        user_query = db.collection('users').where('username', '==', username).get()
        if not user_query:
            db.collection('users').document().set({"username": username})
            return {"username": username}
        return convert_document_to_dict(user_query[0])

    def scrape_and_store_user_absences(self, username, password):
        session_manager = SessionManager(user=username, pwd=password)
        session_manager.login()
        oge_scraper = OgeScraper(session_manager)
        absences = AbsenceService(oge_scraper).getAllAbsences()

        self.store_absences_in_firestore([absence.to_dict() for absence in absences], username)

    def store_absences_in_firestore(self, absences, username):
        user_ref = db.collection('users').where('username', '==', username).get()[0].reference
        subject_type_mapping = {
            'CM': '/subject_type/CM', 'TD': '/subject_type/TD',
            'TP': '/subject_type/TP', 'Projet': '/subject_type/Projet'
        }

        for absence in absences:
            absence.pop('id', None)  # Remove 'id' key if exists
            absence['username'] = user_ref
            absence['subjectType'] = subject_type_mapping.get(absence['subjectType'], absence['subjectType'])

            # Check if absence already exists
            start_date = absence['start_date']
            end_date = absence['end_date']
            existing_absences = db.collection('absences').where('username', '==', user_ref) \
                .where('start_date', '==', start_date).where('end_date', '==', end_date).get()

            # Add absence if not existing
            if not existing_absences:
                db.collection('absences').document().set(absence)