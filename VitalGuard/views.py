from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from .models import User, Patient, Feedback
from .serializers import PatientSerializer, MeasurementSerializer, FeedbackSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

from django.db import connection, DatabaseError
from rest_framework import status
from django.apps import apps
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import os
import os


def index(request):
    return HttpResponse("Welcome to VitalGuard server!")

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if user.check_credentials(password):
                login(request, user)
                return HttpResponse('welcome')
            else:
                # Password is incorrect, handle accordingly
                pass
        except User.DoesNotExist:
            # Username does not exist, handle accordingly
            pass
    return render(request, 'VitalGuard/login.html')

def patient_entry(request):
    return render(request, 'VitalGuard/patient_entry.html')

def process_patient_entry(request):
    if request.method == 'POST':
        p_name = request.POST.get('name')
        p_surname = request.POST.get('surname')
        p_device_tag = request.POST.get('device_tag')
        p_age = request.POST.get('age')
        p_description = request.POST.get('description')
        patient = Patient(name=p_name, surname=p_surname, device_tag=p_device_tag, age=p_age, description=p_description)

        patient.save()
        return HttpResponse('entry added')
    else:
        return HttpResponse('Cannot process request')

class AdminUpdaterView(APIView):
    def get(self, request, format=None):
        content = {}
        return render(request, 'admin-panel/public/ap-updater.html', content)

class AdminDatabaseManagerView(APIView):
    def get(self, request, format=None):
        content = {}
        return render(request, 'admin-panel/public/ap-database-manager.html', content)

class GetSourceDirView(APIView):
    def get(self, request, format=None):
        def get_directory_structure(directory):
            ignore_dirs = ['.pio', '.vscode', '.gitignore', '.git']
            directory_structure = []
            for item_name in os.listdir("source-code/" + directory):
                if item_name in ignore_dirs:
                    continue
                item_path = directory + "/" + item_name if directory != "" else item_name
                if os.path.isdir("source-code/" + item_path):
                    directory_structure.append({"path": item_path, "name": item_name, "type": "dir"})
                elif os.path.isfile("source-code/" + item_path):
                    directory_structure.append({"path": item_path, "name": item_name, "type": "file"})
            return directory_structure

        return JsonResponse(get_directory_structure(request.GET.get('path')), safe=False)

class GetSourceFileView(APIView):
    def get(self, request, format=None):
        filepath = request.GET.get('path')
        with open("source-code/" + filepath, 'r') as file:
            data = file.read()
        return JsonResponse({'data': data})
    
class PatientList(APIView):
    """
    Get all patients (GET), or add new (POST)
    """
    def get(self, request, format=None):
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientData(APIView):
    """
    Get, change or remove patient
    """
    def get_object(self, pk):
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        patient = self.get_object(pk)
        serializer = PatientSerializer(patient, data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        patient = self.get_object(pk)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class MeasurementView(APIView):
    """
    Add new measurement
    """
    def post(self, request, format=None):
        serializer = MeasurementSerializer(data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PairingRequestView(APIView):
    """
    Request device pairing.
    Expected payload: name, surname, device_tag
    """
    def post(self, request, format=None):
        name = request.data['name']
        surname = request.data['surname']
        device_tag = request.data['device_tag']

        if (not name or not surname or not device_tag):
            return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PatientSerializer(data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FeedbackView(APIView):
    """
    Get last feedback per device
    """
    def get_object(self, device_tag):
        try:
            try:
                patient = Patient.objects.filter(device_tag=device_tag).first()
            except Patient.DoesNotExist:
                raise Http404
            feedback = Feedback.objects.filter(patient=patient).first()
            return feedback

        except Feedback.DoesNotExist:
            raise Http404
    
    def get(self, request, format=None):
        feedback = self.get_object(device_tag="asdfgflkgm2o4ing")
        serializer = FeedbackSerializer(feedback)
        
        return Response(serializer.data)
    
class CredentialsCheckView(APIView):
    """
    Check user credentials
    """
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
    

    def post(self, request, format=None):

        username = request.data['username']
        password = request.data['password']

        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.get_object(username)
            if user.check_credentials(password):
                if user.is_caretaker():
                    return HttpResponse('CT')
                elif user.is_doctor():
                    return HttpResponse('DR')
                else:
                    return HttpResponse('NA')
            else:
                return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_403_FORBIDDEN)

        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

class SchemaView(APIView):
    def get(self, request, format=None):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                schema = {}

                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    fields = cursor.fetchall()

                    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                    foreign_keys = cursor.fetchall()

                    if table_name not in schema:
                        schema[table_name] = []

                    for field in fields:
                        field_name = field[1]
                        field_type = field[2]
                        if field[5]: is_pk = True
                        else: is_pk = False
                        related_model = None
                        related_field = None
                        for fk in foreign_keys:
                            if fk[3] == field_name:
                                related_model = fk[2]
                                related_field = fk[4]

                        schema[table_name].append({
                            'name': field_name,
                            'type': field_type,
                            'pk': is_pk,
                            'related_field': related_field,
                            'related_model': related_model
                        })

                return JsonResponse(schema)

        except DatabaseError:
            return Response({'error': 'Failed to retrieve schema details.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ExecuteQueryView(APIView):
    def post(self, request, format=None):
        query = request.data['query']

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                fields = [desc[0] for desc in cursor.description]

            return Response({'fields': fields, 'results': results})

        except DatabaseError:
            return Response({'error': 'Invalid query.'}, status=status.HTTP_400_BAD_REQUEST)