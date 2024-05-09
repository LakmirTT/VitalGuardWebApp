from django.contrib import admin

from .models import Patient, Measurement, User, Threshold, Feedback

admin.site.register(Patient)
admin.site.register(Measurement)
admin.site.register(User)
admin.site.register(Threshold)
admin.site.register(Feedback)