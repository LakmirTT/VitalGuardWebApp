from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = "VitalGuard"

urlpatterns = [
    # ex: /vitalguard
    path("", views.index, name="index"),
    #   add patient via HTML form, for testing only, will remove later
    path('patient_entry/', views.patient_entry, name='patient_entry'),
    path('process_patient_entry/', views.process_patient_entry, name='process_patient_entry'),
    
    # ex: /vitalguard/patients/
    path('api/patients/', views.PatientList.as_view()),
    # ex: /vitalguard/patients/1
    path('api/patients/<int:pk>', views.PatientData.as_view()),

    # ex: /vitalguard/measurement/
    path('api/measurement/', views.MeasurementView.as_view()),

    # ex: /vitalguard/pair_req/xzxzz
    path('api/device/pair_req/', views.PairingRequestView.as_view()),

    # ex: /get_last_feedback/XXXX
    path('api/get_last_feedback/', views.FeedbackView.as_view()),

    #   user entries
    path('api/users/check_credentials/', views.CredentialsCheckView.as_view()),



]

urlpatterns = format_suffix_patterns(urlpatterns)