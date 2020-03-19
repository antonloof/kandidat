import pigpio

from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.http import require_POST

from time import sleep, time

from measure.models import Measurment
from measure.adc_manager import AdcManager, InpmuxOptions
from measure.motor_manager import MotorManager


class MeasurmentManager:
	def __init__(self):
		self.pi = None
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
		self.pi = pigpio.pi()
		self.adc_manager = AdcManager(self.pi)
		self.motor_manager = MotorManager(self.pi)
		return self
		
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.adc_manager.close()
		self.motor_manager.close()
		self.pi.stop()
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

	def setup_offset_measurment(self):
		self.adc_manager.reset()
		# offset calibration gives approx one order of magnitude lower offset voltage
		# compared to input_chop
		self.adc_manager.offset_calibration()
		# self.adc_manager.enable_chop()
		self.adc_manager.set_input_mode(InpmuxOptions.AIN0, InpmuxOptions.AIN1)
		
	def measure_offset(self):
		return self.adc_manager.read_value()
		
	def test_motor(self):
		self.motor_manager.turn(100, micro_step=False, steps_per_second=60)

@require_POST
def start_measurement(request):
	measurment_manager = MeasurmentManager()
	if not measurment_manager.can_measure:
		return HttpResponse('{"error": "Another measurment is in progress. Please wait a bit"}', status=400)
	
	with measurment_manager:
		measurment_manager.setup_temperature_measurment()
		ret = measurment_manager.measure_temperature()
		measurment_manager.test_motor()
		#measurment_manager.setup_offset_measurment()
		#offset = sum([measurment_manager.measure_offset() for _ in range(100)])/100
		offset = 0
		return HttpResponse("{" + '"ost":' + str(ret) + ',"offset": ' + str(offset) + '}')
	