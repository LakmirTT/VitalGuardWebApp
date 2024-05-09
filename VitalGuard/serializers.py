from rest_framework import serializers
from VitalGuard.models import Patient, Measurement

"""
Form encoded input/output for API with respect to each model
"""

class PatientSerializer(serializers.ModelSerializer):
    class Meta():
        model = Patient
        fields = ['name', 'surname', 'device_tag', 'age', 'description']

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta():
        model = Measurement
        fields = ['patient', 'time_taken', 'heart_rate', 'body_temp', 'ox_saturation', 'blood_pressure']