import pigpio

import numpy as np
from scipy.optimize import leastsq, fsolve

from time import sleep, time
from math import sin, pi, asin

from random import random

from threading import Thread

from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.http import require_POST

from rest_framework import viewsets
from rest_framework.response import Response

from measure.models import Measurment, RhValue
from measure.adc_manager import AdcManager, InpmuxOptions, Gain, ReferenceMode
from measure.motor_manager import MotorManager
from measure.serializers import MeasurmentSerializer


B_MAX = 0.3318
STEPS_PER_TURN = 200

def measure_operation(measurment_manager):
	with measurment_manager:
		measurment_manager.set_up_mobility_measurment()
		measurment = measurment_manager.measurment
		
		r_mu_s = []
		steps_per_measurment = 10
		measurment_count = STEPS_PER_TURN / steps_per_measurment
		assert measurment_count == int(measurment_count), "Can only do a multiple of 200"
		
		for _ in range(5):
			measurment_manager.measure_current_and_voltage() # dummy measurment 
		
		for _ in range(int(measurment_count)):
			measurment_manager.advance_motor(steps_per_measurment)
			v, i = measurment_manager.measure_current_and_voltage()
			r_mu_s.append(v / i)
			print(v)
			#sleep(1)
		
		RhValue.objects.bulk_create([RhValue(value=v, measurment=measurment) for v in r_mu_s])
		t = np.linspace(0, STEPS_PER_TURN, len(r_mu_s))
		r_mu_s = np.array(r_mu_s)
		print("y = ", list(r_mu_s), ";")
		# make some educated guesses before letting the math loose :)
		guess_amp = (max(r_mu_s) - min(r_mu_s)) / 2
		guess_phase = asin(r_mu_s[0]/max(abs(r_mu_s)))
		guess_angle_freq = 2*pi/STEPS_PER_TURN
		guess_offset = np.mean(r_mu_s)		

		# let the math loose
		optimize_func = lambda x: x[0]*np.sin(guess_angle_freq*t+x[1]) + x[2] - r_mu_s
		amp,  phase, offset = leastsq(optimize_func, [guess_amp, guess_phase, guess_offset])[0]
		print("a=", amp, ";")
		print("b=", guess_angle_freq, ";")
		print("c=", phase, ";")
		print("d=", offset, ";")
		print("how good it is:", sum(optimize_func([amp,  phase, offset])**2))
		measurment.amplitude = amp
		measurment.angle_freq = guess_angle_freq
		measurment.phase = phase
		measurment.offset = offset
		dr_db = amp/B_MAX
		phase = phase % (2 * pi)
		phase_in_steps = phase * STEPS_PER_TURN / (2 * pi)
		
		# make it take the short way
		if phase_in_steps > STEPS_PER_TURN / 2:
			phase_in_steps = -(STEPS_PER_TURN - phase_in_steps)
			
		print("dr_db:", dr_db)
		print("phase in steps:", phase_in_steps)
		# now the motor is at a minimum of the magnetic flux density
		measurment_manager.advance_motor(-int(round(phase_in_steps)))

		r_mnop = measure_r_for_rs(measurment_manager)
		# Byt kontakter. 
		# Kontakten som varit kopplad till in+ kopplas till jord.
		# Kontakten som varit kopplad till in- kopplas till in+.
		# Kontakten som varit kopplad till strömkällan kopplas till in-
		# Kontakten som varit kopplad till jord kopplas till strömkällan. 

		# in+ och in- beteckanar de två ingångarna till förstärkarsteget 
		# Strömkällan och jord betecknar de kontakter som strömen skickas genom
		
		r_nopm = measure_r_for_rs(measurment_manager)
		print("the r's needed for rs:", r_mnop, r_nopm)
		
		f = lambda rs: np.exp(-pi*r_mnop/rs) + np.exp(-pi*r_nopm/rs) - 1
		df_drs = lambda rs: -pi / rs * (r_mnop * np.exp(-pi * r_mnop / rs) + np.exp(-pi * r_nopm / rs))
		
		reasonable_rs_guess = (r_nopm + r_mnop) / 2
		
		rs = fsolve(f, reasonable_rs_guess, fprime=df_drs)[0]
		print("rs:", rs)
		mu = dr_db/rs
		print("mu:", mu)
		
		measurment.mobility = mu
		measurment.sheet_resistance = rs
		measurment.save()

def measure_r_for_rs(measurment_manager):
	sleep(1)
	v1, i1 = measurment_manager.measure_current_and_voltage()
	r1 = v1/i1

	measurment_manager.advance_motor(STEPS_PER_TURN // 2)
	sleep(1)
	v2, i2 = measurment_manager.measure_current_and_voltage()
	r2 = v2/i2
	
	return (r1 + r2) / 2


class MeasurmentView(viewsets.ModelViewSet):
	queryset = Measurment.objects.all()
	serializer_class = MeasurmentSerializer

	def measure(self, request):
		measurment_manager = MeasurmentManager()
		if not measurment_manager.can_measure:
			return Response('{"error": "Another measurment is in progress. Please wait a bit"}', status=400)
		thread = Thread(target=measure_operation, args=(measurment_manager, ))
		thread.start()
		serializer = self.serializer_class(measurment_manager.measurment)
		return Response(serializer.data)
					

class MeasurmentManager:
	def __init__(self):
		self.pi = None
		self.can_measure = False
		self.adc_manager = None
		self.motor_manager = None
		self.measurment = Measurment()
		self.x = 42 # a random number for testing
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

	def set_up_mobility_measurment(self):
		self.adc_manager.reset()
		self.adc_manager.enable_chop()
		self.adc_manager.set_reference_mode(ReferenceMode.SUPPLY, ReferenceMode.SUPPLY)
		self.adc_manager.start()
	
	def setup_current_measurment(self):
		self.adc_manager.set_input_mode(InpmuxOptions.AIN2, InpmuxOptions.AIN3)
		
	def setup_voltage_measurment(self):
		self.adc_manager.set_input_mode(InpmuxOptions.AIN0, InpmuxOptions.AIN1)
		
	def measure_voltage(self):
		#self.x += 2 # used for test
		#return sin(self.x/200 * 2 * pi) * B_MAX * (1 + (random() - 0.5) * 2 / 100) # used for test
		return (self.adc_manager.read_value() * 10 - 2.5) / 100

	def measure_current(self):
		shunt_resistance = 9920
		return self.adc_manager.read_value() / shunt_resistance * 10
		
	def measure_current_and_voltage(self):
		self.setup_voltage_measurment()
		v = self.measure_voltage()
		self.setup_current_measurment()
		i = 10e-6 # used until we get this from the outside
		#i = self.measure_current()
		return v, i
		
	def advance_motor(self, steps):
		return #tmp for test
		speed = min(10, abs(steps))
		self.motor_manager.turn(steps, micro_step=True, steps_per_second=speed)		
