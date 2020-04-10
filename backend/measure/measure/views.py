import pigpio

import numpy as np

from time import sleep, time
from math import sin, pi, asin
from scipy.optimize import leastsq, fsolve
from threading import Thread

from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response

from measure.models import Measurement, RhValue
from measure.serializers import MeasurementSerializer, RhValueSerializer
from measure.filters import RhValueFilter, MeasurementFilter
from measure.measurement_manager import MeasurementManager


B_MAX = 0.3318
STEPS_PER_TURN = 200


def measure_operation(measurement_manager):
    with measurement_manager:
        measurement_manager.set_up_mobility_measurement()
        measurement = measurement_manager.measurement
        r_mu_s = []

        for _ in range(5):
            measurement_manager.measure_current_and_voltage()  # dummy measurement

        measurement_count = STEPS_PER_TURN // measurement.steps_per_measurement
        for _ in range(measurement_count):
            measurement_manager.advance_motor(measurement.steps_per_measurement)
            v, i = measurement_manager.measure_current_and_voltage()
            r_mu_s.append(v / i)
            print(v)
            # sleep(1)

        RhValue.objects.bulk_create([RhValue(value=v, measurement=measurement) for v in r_mu_s])
        t = np.linspace(0, STEPS_PER_TURN, len(r_mu_s))
        r_mu_s = np.array(r_mu_s)
        print("y = ", list(r_mu_s), ";")
        # make some educated guesses before letting the math loose :)
        guess_amp = (max(r_mu_s) - min(r_mu_s)) / 2
        guess_phase = asin(r_mu_s[0] / max(abs(r_mu_s)))
        guess_angle_freq = 2 * pi / STEPS_PER_TURN
        guess_offset = np.mean(r_mu_s)

        # let the math loose
        optimize_func = lambda x: x[0] * np.sin(guess_angle_freq * t + x[1]) + x[2] - r_mu_s
        amp, phase, offset = leastsq(optimize_func, [guess_amp, guess_phase, guess_offset])[0]
        print("a=", amp, ";")
        print("b=", guess_angle_freq, ";")
        print("c=", phase, ";")
        print("d=", offset, ";")
        print("how good it is:", sum(optimize_func([amp, phase, offset]) ** 2))
        measurement.amplitude = amp
        measurement.angle_freq = guess_angle_freq
        measurement.phase = phase
        measurement.offset = offset
        dr_db = amp / B_MAX
        phase = phase % (2 * pi)
        phase_in_steps = phase * STEPS_PER_TURN / (2 * pi)

        # make it take the short way
        if phase_in_steps > STEPS_PER_TURN / 2:
            phase_in_steps = -(STEPS_PER_TURN - phase_in_steps)

        print("dr_db:", dr_db)
        print("phase in steps:", phase_in_steps)
        # now the motor is at a minimum of the magnetic flux density
        measurement_manager.advance_motor(-int(round(phase_in_steps)))

        r_mnop = measure_r_for_rs(measurement_manager)
        # Byt kontakter.
        # Kontakten som varit kopplad till in+ kopplas till jord.
        # Kontakten som varit kopplad till in- kopplas till in+.
        # Kontakten som varit kopplad till strömkällan kopplas till in-
        # Kontakten som varit kopplad till jord kopplas till strömkällan.

        # in+ och in- beteckanar de två ingångarna till förstärkarsteget
        # Strömkällan och jord betecknar de kontakter som strömen skickas genom

        r_nopm = measure_r_for_rs(measurement_manager)
        print("the r's needed for rs:", r_mnop, r_nopm)

        f = lambda rs: np.exp(-pi * r_mnop / rs) + np.exp(-pi * r_nopm / rs) - 1
        df_drs = (
            lambda rs: -pi / rs * (r_mnop * np.exp(-pi * r_mnop / rs) + np.exp(-pi * r_nopm / rs))
        )

        reasonable_rs_guess = (r_nopm + r_mnop) / 2

        rs = fsolve(f, reasonable_rs_guess, fprime=df_drs)[0]
        print("rs:", rs)
        mu = dr_db / rs
        print("mu:", mu)

        measurement.mobility = mu
        measurement.sheet_resistance = rs
        measurement.save()


def measure_r_for_rs(measurement_manager):
    sleep(1)
    v1, i1 = measurement_manager.measure_current_and_voltage()
    r1 = v1 / i1

    measurement_manager.advance_motor(STEPS_PER_TURN // 2)
    sleep(1)
    v2, i2 = measurement_manager.measure_current_and_voltage()
    r2 = v2 / i2

    return (r1 + r2) / 2


class MeasurementView(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    filter_class = MeasurementFilter
    ordering = ["-open", "-created_at"]

    def measure(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        measurement_manager = MeasurementManager(serializer)
        if not measurement_manager.can_measure:
            return Response(
                '{"error": "Another measurement is in progress. Please wait a bit"}', status=400,
            )
        thread = Thread(target=measure_operation, args=(measurement_manager,))
        thread.start()
        serializer = self.serializer_class(measurement_manager.measurement)
        return Response(serializer.data)


class RhValueView(viewsets.ModelViewSet):
    queryset = RhValue.objects.all()
    serializer_class = RhValueSerializer
    filter_class = RhValueFilter
    ordering = "-measurement_id"
