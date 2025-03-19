from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Patient(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    insurance = models.ForeignKey('Insurance', on_delete=models.SET_NULL, null=True, blank=True)
    policy_number = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"{self.user_profile}"


class Administrator(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admin: {self.user_profile}"


class Doctor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.name}"


class Insurance(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.doctor}"


class InsuranceService(models.Model):
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    covered = models.BooleanField(default=False)

    class Meta:
        unique_together = ('insurance', 'service')

    def __str__(self):
        return f"{self.insurance} - {self.service}: {'Covered' if self.covered else 'Not Covered'}"


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField()

    APPOINTMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    appointment_status = models.CharField(max_length=10, choices=APPOINTMENT_STATUS_CHOICES, default='pending')

    INSURANCE_AUTHORIZATION_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    insurance_authorization_status = models.CharField(max_length=8, choices=INSURANCE_AUTHORIZATION_CHOICES,
                                                      default='pending')

    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment {self.id} - {self.patient} - {self.service} ({self.appointment_status})"


class Reminder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    send_datetime = models.DateTimeField()

    def __str__(self):
        return f"Reminder {self.id} - {self.patient} - {self.appointment}"


class Notification(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    administrator = models.ForeignKey(Administrator, on_delete=models.CASCADE)
    notification_datetime = models.DateTimeField(auto_now_add=True)

    ACTION_TYPE_CHOICES = [
        ('modification', 'Modification'),
        ('cancellation', 'Cancellation'),
    ]
    action_type = models.CharField(max_length=12, choices=ACTION_TYPE_CHOICES)

    def __str__(self):
        return f"Notification {self.id} - {self.appointment} ({self.action_type})"
