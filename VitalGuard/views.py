from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from .models import User, Patient, Feedback, Measurement
from .serializers import PatientSerializer, MeasurementSerializer, FeedbackSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
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
    
def admin_index(request):
    content = {}
    return render(request, 'admin-panel/public/ap-index.html', content)

def admin_updater(request):
    content = {}
    return render(request, 'admin-panel/public/ap-updater.html', content)

def get_source_filenames(request):
    return JsonResponse({'filenames': os.listdir('admin-panel/versions-source')})

def get_source_file(request):
    filename = request.GET.get('filename')
    with open('admin-panel/versions-source/' + filename, 'r') as file:
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

class MeasurementListView(APIView):
    """
    Get all measurements per patient
    """
    def get(self, request, format=None):
        id = request.data['id']
        if (not id):
            return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
        measurements = Measurement.objects.filter(patient=id)
        serializer = MeasurementSerializer(measurements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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
