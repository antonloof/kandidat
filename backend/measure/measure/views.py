import pigpio

import numpy as np

from time import sleep, time
from math import sin, pi, asin
from scipy.optimize import leastsq, fsolve
from threading import Thread

from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response

from measure.models import Measurment, RhValue
from measure.serializers import MeasurmentSerializer, RhValueSerializer
from measure.filters import RhValueFilter, MeasurmentFilter
from measure.measurment_manager import MeasurmentManager


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
	filter_class = MeasurmentFilter

	def measure(self, request):
		measurment_manager = MeasurmentManager()
		if not measurment_manager.can_measure:
			return Response('{"error": "Another measurment is in progress. Please wait a bit"}', status=400)
		thread = Thread(target=measure_operation, args=(measurment_manager, ))
		thread.start()
		serializer = self.serializer_class(measurment_manager.measurment)
		return Response(serializer.data)


class RhValueView(viewsets.ModelViewSet):
	queryset = RhValue.objects.all()
	serializer_class = RhValueSerializer
	filter_class = RhValueFilter
