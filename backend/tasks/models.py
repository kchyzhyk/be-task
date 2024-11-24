from django.db import models
from django.contrib.auth.models import User

class GeocodeAddress(models.Model):
    formatted_address = models.CharField(max_length=255, null=False, blank=True)

    def __str__(self):
        return self.formatted_address


class UtilityRate(models.Model):
    geocode_address = models.ForeignKey(GeocodeAddress, related_name='utility_rates', on_delete=models.CASCADE)
    utility_name = models.CharField(max_length=255)
    schedule_name= models.CharField(max_length=255, null=True, blank=True)
    startdate = models.DateField()
    enddate = models.DateField(null=True, blank=True)
    uri = models.URLField(null=True, blank=True)
    pricing_matrix = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.utility_name} - {self.startdate} to {self.enddate or 'Present'}"


class WeekdaySchedule(models.Model):
    utility_rate = models.ForeignKey(UtilityRate, related_name='schedules', on_delete=models.CASCADE)
    month = models.CharField(max_length=255)
    values = models.JSONField()

    def __str__(self):
        return f"Schedule for {self.month} ({self.utility_rate.utility_name})"


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    address = models.CharField(max_length=255)
    utility_rate = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address} ({self.user.username})"


class Tariff(models.Model):
    utility_rate = models.ForeignKey(UtilityRate, related_name='tariffs', on_delete=models.CASCADE)
    month = models.CharField(max_length=255)
    day_period = models.CharField(max_length=50, choices=[('day', 'Day'), ('night', 'Night')]) 
    hour_start = models.IntegerField()
    hour_end = models.IntegerField()
    rate_per_kwh = models.DecimalField(max_digits=5, decimal_places=4)

    def __str__(self):
        return f"Tariff for {self.utility_rate.utility_name} in {self.month} ({self.day_period})"