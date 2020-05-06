from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Measurement(models.Model):
    name = models.CharField(max_length=100)
    error = models.TextField(default="")

    open = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    mobility = models.FloatField(null=True)
    sheet_resistance = models.FloatField(null=True)
    amplitude = models.FloatField(null=True)
    angle_freq = models.FloatField(null=True)
    phase = models.FloatField(null=True)
    offset = models.FloatField(null=True)

    current_limit = models.FloatField()
    connection_1 = models.IntegerField()
    connection_2 = models.IntegerField()
    connection_3 = models.IntegerField()
    connection_4 = models.IntegerField()
    steps_per_measurement = models.IntegerField()


class RhValue(models.Model):
    value = models.FloatField()
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    angle = models.FloatField()
