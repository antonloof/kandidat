from django.db import models
from django.utils import timezone


class Measurment(models.Model):
    open = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    mobility = models.FloatField(null=True)
    sheet_resistance = models.FloatField(null=True)
    amplitude = models.FloatField(null=True)
    angle_freq = models.FloatField(null=True)
    phase = models.FloatField(null=True)
    offset = models.FloatField(null=True)


class RhValue(models.Model):
    value = models.FloatField()
    measurment = models.ForeignKey(Measurment, on_delete=models.CASCADE)
