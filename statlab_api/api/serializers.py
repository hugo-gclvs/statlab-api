from .utils.firestore_utils import db
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
        token = RefreshToken.for_user(user)
        # Ajoutez des informations personnalisées au jeton ici, si nécessaire
        token['username'] = user.username
        return token

    def validate(self, attrs):
        # Ici, vous pouvez intégrer votre logique personnalisée pour valider les utilisateurs.
        # Par exemple, vérifiez si l'utilisateur existe dans Firestore.
        username = attrs.get('username')
        password = attrs.get('password')

        if not user_is_valid(username, password):  # Votre fonction de validation personnalisée
            raise AuthenticationFailed('No active account found with the given credentials')

        user = db.collection('users').where('username', '==', username).get()
        if len(user) == 0:
            # Si non, créez un nouvel utilisateur
            user_ref = db.collection('users').document()
            user_ref.set({"username": username})


        print(user.username)

        refresh = self.get_token(user)

        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data
    
def user_is_valid(username, password):
    session_manager = SessionManager(user=username, pwd=password)

    if session_manager.login():
        return True
    else:
        return False