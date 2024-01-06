import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Absence, User
from .serializers import AbsenceSerializer, UserSerializer
from firebase_admin import firestore
from django.http import JsonResponse

db = firestore.client()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request):
        users = db.collection('users').get()
        return Response([convertir_document_en_dict(user) for user in users])

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Utilise la méthode create() du serializer
            return Response(user)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        user_existante = get_user_details(pk)
        serializer = UserSerializer(user_existante, data=request.data)
        if serializer.is_valid():
            user_mise_a_jour = serializer.save()  # Utilise la méthode update() du serializer
            return Response(user_mise_a_jour)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def absences(self, request, pk=None):
        absences = recuperer_absences_par_utilisateur(pk)  # Récupérer les absences de Firestore
        serializer = AbsenceSerializer(absences, many=True)  # Sérialiser les données
        return Response(serializer.data)

def recuperer_absences_par_utilisateur(username):
    try:
        absences_ref = db.collection('absences').where('username', '==', username)
        absences = absences_ref.get()
        return [convertir_document_en_dict(absence) for absence in absences]
    except Exception as e:
        # Handle any errors
        pass

class AbsenceViewSet(viewsets.ModelViewSet):
    serializer_class = AbsenceSerializer
    queryset = Absence.objects.all()

    def list(self, request):
        absences = recuperer_absences()  # Récupérer les absences de Firestore
        print(absences)
        serializer = AbsenceSerializer(absences, many=True)  # Sérialiser les données
        return Response(serializer.data) 

    def create(self, request):
        serializer = AbsenceSerializer(data=request.data)
        if serializer.is_valid():
            absence = serializer.save()  # Utilise la méthode create() du serializer
            return Response(absence)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        absence_existante = recuperer_absence_par_id(pk)
        serializer = AbsenceSerializer(absence_existante, data=request.data)
        if serializer.is_valid():
            absence_mise_a_jour = serializer.save()  # Utilise la méthode update() du serializer
            return Response(absence_mise_a_jour)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        # Logique pour supprimer une absence de Firestore
        return Response({'message': 'Absence supprimée avec succès!'})

def recuperer_absence_par_id(id):
    try:
        absence_ref = db.collection('absences').document(id)
        absence = absence_ref.get()
        return convertir_document_en_dict(absence)
    except Exception as e:
        # Handle any errors
        pass

def convertir_document_en_dict(document):
    """ Convertit un DocumentSnapshot Firestore en dictionnaire. """
    dict_document = document.to_dict()
    dict_document['id'] = document.id

    # Convertir les DocumentReference en ID
    user_ref = dict_document.get('username') or dict_document.get('users')
    if isinstance(user_ref, firestore.DocumentReference):
        user_details = get_user_details(user_ref)
        dict_document['username'] = user_details.get('username') if user_details else None
    else:
        dict_document['username'] = user_ref if user_ref else None

    # Gérer la référence 'subjectType'
    subject_type_ref = dict_document.get('subjectType')
    if isinstance(subject_type_ref, firestore.DocumentReference):
        subject_type_details = get_subject_type_details(subject_type_ref)
        dict_document['subjectType'] = subject_type_details.get('type') if user_details else None
    else:
        dict_document['subjectType'] = subject_type_ref if subject_type_ref else None


    # Convertir les dates
    for key, value in dict_document.items():
        if isinstance(value, datetime.datetime):
            dict_document[key] = value.isoformat()


    return dict_document

def recuperer_absences():
    try:
        absences_ref = db.collection('absences')
        absences = absences_ref.get()
        return [convertir_document_en_dict(absence) for absence in absences]
    except Exception as e:
        # Handle any errors
        pass

def get_user_details(user_ref):
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None

def get_subject_type_details(subject_type_ref):
    subject_type_doc = subject_type_ref.get()
    if subject_type_doc.exists:
        return subject_type_doc.to_dict()
    return None
