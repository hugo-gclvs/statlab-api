from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from api.models import Absence
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers import GroupSerializer, UserSerializer, AbsenceSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# class AbsenceViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows absences to be viewed or edited.
#     """
#     queryset = Absence.objects.all()
#     serializer_class = AbsenceSerializer
#     permission_classes = [permissions.IsAuthenticated]


class AbsenceList(APIView):
    """
    List all absences, or create a new absence.
    """
    def get(self, request, format=None):
        absences = get_absences_from_source()
        serializer = AbsenceSerializer(absences, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AbsenceSerializer(data=request.data)
        if serializer.is_valid():
            absence = serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
def get_absences_from_source():
    # Exemple de données récupérées - remplacer par votre propre logique
    return [
        Absence(
            id="abs001",
            subject="Mathematics",
            subjectType="Lecture",
            classroom="101A",
            teacher="M. Dupont",
            start_date=datetime.timestamp(datetime(2021, 5, 15, 9, 0)),
            end_date=datetime.timestamp(datetime(2021, 5, 15, 10, 30)),
            justification="Sick leave"
        ),
        # ... autres instances d'Absence ...
    ]