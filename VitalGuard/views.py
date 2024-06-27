from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from .models import User, Patient, Feedback, Measurement
from .serializers import PatientSerializer, MeasurementSerializer, FeedbackSerializer, UserSerializer, PatientIdSerializer, UserIdSerializer

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
import shutil
import subprocess


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
    
class GetDeployedVersionView(APIView):
    def get(self, request, format=None):
        with open("deployed-source/deployed_version.txt", 'r') as file:
            version = file.read()
        return JsonResponse({'version': version})
        
class CreateNewVersionDirView(APIView):
    def post(self, request, format=None):
        dupe_dir = request.data['dupe_dir']
        if dupe_dir != "" and dupe_dir not in os.listdir("source-code"):
            return HttpResponse('Dupe version directory does not exist.', status=status.HTTP_400_BAD_REQUEST)

        new_dir = request.data['new_dir']
        if new_dir in os.listdir("source-code"):
            return HttpResponse('A version directory with this name already exists.', status=status.HTTP_400_BAD_REQUEST)
        if dupe_dir != "":
            shutil.copytree(f"source-code/{dupe_dir}", f"source-code/{new_dir}")
        else:
            os.system(f"mkdir .\\source-code\\{new_dir}")
        return HttpResponse('New version directory created succesfully.', status=status.HTTP_200_OK)
    
class DeployVersionView(APIView):
    def get(self, request, format=None):
        version = request.GET.get('version')
        if not os.path.isfile(f"source-code/{version}/platformio.ini"):
            return HttpResponse('Invalid PlatformIO project.', status=status.HTTP_400_BAD_REQUEST)
        result = self.compile_platformio_project(f"source-code\\{version}")
        if not result['success']:
            return HttpResponse(result['error'], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        shutil.copyfile(result['bin_file'], "deployed-source/firmware.bin")
        with open("deployed-source/deployed_version.txt", 'w') as file:
            file.write(version)
        return HttpResponse('Version deployed succesfully.', status=status.HTTP_200_OK)

    def compile_platformio_project(self, project_dir):
        try:
            print('Compiling PlatformIO project:', project_dir)
            if not os.path.exists(os.path.join(project_dir, 'platformio.ini')):
                return {'success': False, 'error': 'Invalid PlatformIO project'}

            result = subprocess.run(['platformio', 'run'], cwd=project_dir, capture_output=True, text=True)

            if result.returncode != 0:
                return {'success': False, 'error': result.stderr}

            bin_file = os.path.join(project_dir, '.pio', 'build', 'ttgo-lora32-v1', 'firmware.bin')
            print('Compiled .bin file:', bin_file)

            if not bin_file:
                return {'success': False, 'error': 'Compiled .bin file not found'}

            return {'success': True, 'bin_file': bin_file}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    
class CreateNewFileView(APIView):
    def get(self, request, format=None):
        try:
            filepath = request.GET.get('path')
            print(filepath)
            os.makedirs(os.path.dirname("source-code/" + filepath), exist_ok=True)
            with open("source-code/" + filepath, 'w') as file:
                file.write("")
            return HttpResponse('New file created successfully.', status=status.HTTP_200_OK)
        except Exception as e:
            return HttpResponse('An error occurred while creating file', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SaveSourceFileView(APIView):
    def post(self, request, format=None):
        try:
            filepath = request.data['path']
            data = request.data['data']
            with open("source-code/" + filepath, 'w') as file:
                file.write(data)
            return HttpResponse('File content updated successfully.', status=status.HTTP_200_OK)
        except Exception as e:
            return HttpResponse('An error occurred while updating file', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    Expected payload: device_tag
    """
    def post(self, request, format=None):
        device_tag = request.data['device_tag']

        if (not device_tag):
            return Response({'detail': 'Device tag expected!'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:    # patient exists, OK
            patient = Patient.objects.get(device_tag=device_tag)
            patient.is_paired = True;
            patient.save()
            return Response({'detail': 'Pairing OK'}, status=status.HTTP_200_OK)
                 
        except Patient.DoesNotExist:    # no patient return error        
            return Response({'detail': 'Illigitimate device tag, pairing denied.'}, status=status.HTTP_404_NOT_FOUND)

            
    
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
    def get_object(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise Http404
    

    def post(self, request, format=None):

        email = request.data['email']
        password = request.data['password']

        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.get_object(email)
            user_id = user.pk
            if user.check_credentials(password):
                if user.is_caretaker():
                    #patient_ids = Patient.objects.filter(caretaker_id=user_id).values_list('pk', flat=True)
                    #rel_doctors = User.objects.filter(user_type='DR', pk__in=p)
                    rel_doctors = Patient.objects.filter(caretaker=user_id)
                    doctor_serializer = UserIdSerializer(rel_doctors, many=True)
                    return Response({'type': 'CT', 'data': doctor_serializer.data}, status=status.HTTP_200_OK)
                elif user.is_doctor():
                    rel_ctkrs = Patient.objects.filter(doctor=user_id)
                    ctkr_serializer = UserIdSerializer(rel_ctkrs, many=True)
                    return Response({'type': 'DR', 'data': ctkr_serializer.data}, status=status.HTTP_200_OK)
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