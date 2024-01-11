from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .utils.firestore_utils import db
from rest_framework.exceptions import AuthenticationFailed
from .user_wrapper import FirestoreUser

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            # Ici, nous utilisons 'user_id' comme nom de champ dans le jeton, mais vous devez l'ajuster selon votre implémentation
            user_id = validated_token.get('user_id')  

            # Récupération de l'utilisateur à partir de Firestore en utilisant l'ID
            user_document = db.collection('users').document(user_id).get()
            if user_document.exists:
                return FirestoreUser(user_document.to_dict())
            else:
                raise AuthenticationFailed('User not found')

        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')