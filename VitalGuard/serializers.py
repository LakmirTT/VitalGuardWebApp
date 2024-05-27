from rest_framework import serializers
from VitalGuard.models import Patient, Measurement, User, Threshold, Feedback

"""
Form encoded input/output for API with respect to each model
"""

class PatientSerializer(serializers.ModelSerializer):
    #name = serializers.CharField(max_length=25, required=False)
    #surname = serializers.CharField(max_length=25, required=False)
    
    class Meta():
        model = Patient
        fields = ['name', 'surname', 'device_tag', 'age', 'description', 'is_paired']

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta():
        model = Measurement
        fields = ['patient', 'time_taken', 'heart_rate', 'body_temp', 'ox_saturation', 'blood_pressure']

class UserSerializer(serializers.ModelSerializer):
    """
    will be used for adding users, type and patient are to be assigned by admin
    """
    class Meta():
        model = User
        fields = ['name', 'username', 'password']

class ThresholdSerializer(serializers.Serializer):
    class Meta():
        model = Threshold
        fields = ['patient', 'time_changed', 'heart_rate', 'body_temp', 'ox_saturation', 'blood_pressure']

class FeedbackSerializer(serializers.Serializer):
    class Meta():
        model = Feedback
        fields = ['patient', 'doctor', 'header', 'text', 'time']