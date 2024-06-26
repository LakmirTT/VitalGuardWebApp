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
    path('api/users/get_measurements/', views.MeasurementView.as_view()),

    path('api/get_schema/', views.SchemaView.as_view(), name='get_schema'),


    path('admin/updater/', views.AdminUpdaterView.as_view(), name='admin_updater'),
    path('admin/database_manager/', views.AdminDatabaseManagerView.as_view(), name='admin_database_manager'),

    path('api/device/get_source_dir/', views.GetSourceDirView.as_view(), name='get_source_filenames'),
    path('api/device/get_source_file/', views.GetSourceFileView.as_view(), name='get_source_file'),
    path('api/device/get_deployed_version/', views.GetDeployedVersionView.as_view(), name='get_deployed_version'),
    path("api/device/create_new_version_dir/", views.CreateNewVersionDirView.as_view(), name="create_new_version_dir"),
    path('api/device/create_new_file/', views.CreateNewFileView.as_view(), name='create_new_file'),
    path('api/device/save_source_file/', views.SaveSourceFileView.as_view(), name='save_source_file'),
    path('api/device/deploy_version/', views.DeployVersionView.as_view(), name='deploy_version'),

    path('api/execute_query/', views.ExecuteQueryView.as_view(), name='execute_query'),
]

urlpatterns = format_suffix_patterns(urlpatterns)