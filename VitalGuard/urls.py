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
    
    #   device entries

    # ex: /vitalguard/patients/
    path('api/patients/', views.PatientList.as_view()),
    # ex: /vitalguard/patients/1
    path('api/patients/<int:pk>', views.PatientData.as_view()),

    # ex: /vitalguard/measurement/
    path('api/measurement/', views.MeasurementView.as_view()),

    # see README
    path('api/device/pair_req/', views.PairingRequestView.as_view()),

    # ex: /get_last_feedback/XXXX
    path('api/get_last_feedback/', views.FeedbackView.as_view()),

    #   user entries
    # credentials check
    path('api/users/check_credentials/', views.CredentialsCheckView.as_view()),
    # get measurements for all patients
    path('api/users/get_measurements/', views.MeasurementListView.as_view()),


    path('admin/index/', views.admin_index, name='admin_index'),
    path('admin/updater/', views.admin_updater, name='admin_updater'),
    path('admin/database_manager/', views.admin_database_manager, name='admin_database_manager'),

    path('admin/get_source_filenames/', views.get_source_filenames, name='get_source_filenames'),
    path('admin/get_source_file/', views.get_source_file, name='get_source_file'),
]

urlpatterns = format_suffix_patterns(urlpatterns)