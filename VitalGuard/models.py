from django.db import models
import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# This file represents database architecture

class Patient(models.Model):
    def __str__(self):
        return '%s %s %d y.o.' % (self.name, self.surname, self.age)
    
    # fields
    name = models.CharField(max_length=25, blank=True)
    surname = models.CharField(max_length=25, blank=True)
    device_tag = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(default=0, blank=True)
    description = models.CharField(max_length=200, blank=True)
    is_paired = models.BooleanField(default=False)

class Measurement(models.Model):
    def __str__(self):
        return '%s - %s' % (self.time_taken, self.patient)
    
    # fields
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    time_taken = models.DateTimeField("time taken")
    heart_rate = models.IntegerField(default=0)
    body_temp = models.IntegerField(default=0)
    ox_saturation = models.IntegerField(default=0)
    blood_pressure = models.IntegerField(default=0)

class User(models.Model):
    def __str__(self):
        return '%s %s' % (self.user_type, self.name)
    
    def is_doctor(self):
        return self.user_type == 'DR'
    
    def is_caretaker(self):
        return self.user_type == 'CT'
    
    def check_credentials(self, password):
        return (self.password == password)

    
    # fields
    name = models.CharField(max_length=25)
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=25)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    # enum
    class UserType(models.TextChoices):
        CARETAKER = "CT", _("Caretaker")
        DOCTOR = "DR", _("Doctor")
    
    user_type = models.CharField(
        max_length=2,
        choices=UserType,
        default=UserType.DOCTOR
    )


class Threshold(models.Model):
    def __str__(self):
        return '%s: %s' % (self.patient, self.time_changed)
    
    # fields
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    time_changed = models.DateTimeField("time changed")
    heart_rate = models.IntegerField(default=100)
    body_temp = models.IntegerField(default=100)
    ox_saturation = models.IntegerField(default=100)
    blood_pressure = models.IntegerField(default=100)

    def was_changed_recently(self):
        return self.time_changed >= timezone.now() - datetime.timedelta(days=1)
    
class Feedback(models.Model):
    def __str__(self):
        return 'FROM: %s TO: %s ON: %s' % (self.doctor, self.patient, self.time)
    
    # fields
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    header = models.CharField(max_length=20)
    text = models.CharField(max_length=300)
    time = models.DateField("date posted")