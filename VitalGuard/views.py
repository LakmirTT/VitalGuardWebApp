from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from .models import User, Patient
from .serializers import PatientSerializer, MeasurementSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser


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
    Request device pairing
    """
    def post(self, request, format=None):
        serializer = PatientSerializer(data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)