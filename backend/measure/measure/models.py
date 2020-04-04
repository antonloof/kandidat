from django.db import models
from django.utils import timezone

class Measurment(models.Model):
	open = models.BooleanField(default=True)
	created_at = models.DateTimeField(default=timezone.now)
	mobility = models.FloatField(null=True)
	sheet_resistance = models.FloatField(null=True)
	a = models.FloatField(null=True, help_text="y=a*sin(b*t+c)+d")
	b = models.FloatField(null=True)
	c = models.FloatField(null=True)
	d = models.FloatField(null=True)
		
	
class Unit(models.TextChoices):
	VOLT = "V", "Volt"
	AMPERE = "A", "Ampere"

class DataPoint(models.Model):
	value = models.FloatField()
	measurment = models.ForeignKey(Measurment, on_delete=models.CASCADE)
	unit = models.CharField(max_length=10, choices=Unit.choices)
	purpose = models.CharField(max_length=10)

