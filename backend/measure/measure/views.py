import pigpio

from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.http import require_POST
from time import sleep, time

from measure.models import Measurment
from measure.adc_manager import AdcManager, InpmuxOptions

class MeasurmentManager:
	def __init__(self):
		self.pi = None
		self.spi = None
		self.can_measure = False
		self.adc_manager = None
		self.motor_manager = None
		self.measurment = Measurment()
		
		open_measurments = Measurment.objects.select_for_update().filter(open=True)
		with transaction.atomic():
			self.can_measure = not open_measurments.exists()
			if self.can_measure:
				self.measurment.save()
				
	def __enter__(self):
		pi = pigpio.pi()
		spi = pi.spi_open(0, 50000, 1)
		self.adc_manager = AdcManager(pi, spi)
		return self
		
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.adc_manager.close()
		self.measurment.open = False
		self.measurment.save()
		
	def setup_temperature_measurment(self):
		self.adc_manager.reset()
		self.adc_manager.offset_calibration()
		self.adc_manager.set_input_mode(InpmuxOptions.TEMP_SENS, InpmuxOptions.TEMP_SENS)
		
	def measure_temperature(self):
		value = self.adc_manager.read_value()
		TEMPERATURE_OFFSET = 25
		TEMPERATURE_OFFSET_VALUE = 0.1224
		TEMPERATURE_VOLT_PER_CELCIUS = 0.00042
		return TEMPERATURE_OFFSET + (value - TEMPERATURE_OFFSET_VALUE) / TEMPERATURE_VOLT_PER_CELCIUS

	def measure_offset(self):
		pass

@require_POST
def start_measurement(request):
	measurment_manager = MeasurmentManager()
	if not measurment_manager.can_measure:
		return HttpResponse('{"error": "Another measurment is in progress. Please wait a bit"}', status=400)
	
	with measurment_manager:
		measurment_manager.setup_temperature_measurment()
		ret = measurment_manager.measure_temperature()
		return HttpResponse("{" + '"ost":' + str(ret) + "}")
	