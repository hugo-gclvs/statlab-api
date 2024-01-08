from .utils.firestore_utils import convert_document_to_dict, db
from rest_framework import serializers
from api.models import Absence, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from services.session_manager import SessionManager
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
        # Créez un jeton de rafraîchissement avec des informations utilisateur supplémentaires ici si nécessaire
        token = RefreshToken()
        # Ajoutez des informations personnalisées au jeton ici, si nécessaire
        token['username'] = user['username']
        return token

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Logique de validation de l'utilisateur
        if not user_is_valid(username, password):
            raise AuthenticationFailed('No active account found with the given credentials')

        # Récupérer ou créer l'utilisateur dans Firestore
        user_query = db.collection('users').where('username', '==', username).get()
        if len(user_query) == 0:
            user_ref = db.collection('users').document()
            user_ref.set({"username": username})
            user = {"username": username}
        else:
            user = convert_document_to_dict(user_query[0])

        # Créer les jetons
        refresh = self.get_token(user)

        data = {'refresh': str(refresh), 'access': str(refresh.access_token)}

        return data
    
def user_is_valid(username, password):
    session_manager = SessionManager(user=username, pwd=password)

    if session_manager.login():
        return True
    else:
        return False