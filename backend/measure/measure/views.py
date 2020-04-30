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


def place_resistance_in_bucket(ra, rb, is_rb, r):
    if is_rb:
        rb.append(r)
    else:
        ra.append(r)


def measure_r_for_rs(measurement_manager, connections):
    ra = []
    rb = []
    for index in range(4):
        command = measurement_manager.mux_manager.command()
        command.vp = connections[index]
        command.vn = connections[(index + 1) % 4]
        command.cp = connections[(index + 2) % 4]
        command.cn = connections[(index + 3) % 4]
        command.send()
        v, i = measurement_manager.measure_current_and_voltage()
        is_rb = (
            abs(index - ((index + 1) % 4)) != 1 or abs(((index + 2) % 4) - ((index + 3) % 4)) != 1
        )
        place_resistance_in_bucket(ra, rb, is_rb, -v / i)

        command = measurement_manager.mux_manager.command()
        command.vp = connections[index]
        command.vn = connections[(index - 1) % 4]
        command.cp = connections[(index - 2) % 4]
        command.cn = connections[(index - 3) % 4]
        command.send()
        v, i = measurement_manager.measure_current_and_voltage()
        is_rb = (
            abs(index - ((index - 1) % 4)) != 1 or abs(((index - 2) % 4) - ((index - 3) % 4)) != 1
        )
        place_resistance_in_bucket(ra, rb, is_rb, -v / i)
    print(ra, rb)
    return sum(ra) / len(ra), sum(rb) / len(rb)


class MeasurementView(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    filter_class = MeasurementFilter
    ordering = ["-open", "-created_at"]

    def measure(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.measurement_manager = MeasurementManager(serializer)
        if not self.measurement_manager.can_measure:
            return Response(
                '{"error": "Another measurement is in progress. Please wait a bit"}', status=400,
            )
        thread = Thread(target=self.measure_operation)
        thread.start()
        serializer = self.serializer_class(self.measurement_manager.measurement)
        return Response(serializer.data)

    def measure_operation(self):
        with self.measurement_manager:
            self.measurement_manager.begin()
            self.measurement_manager.set_up_mobility_measurement()
            measurement = self.measurement_manager.measurement
            r_mu_s = []
            measurement_count = STEPS_PER_TURN // measurement.steps_per_measurement
            for _ in range(measurement_count):
                sleep(0.5)
                self.measurement_manager.advance_motor(measurement.steps_per_measurement)
                v, i = self.measurement_manager.measure_current_and_voltage()
                r_mu_s.append(v / i)
                print(v)

            RhValue.objects.bulk_create(
                [
                    RhValue(value=v, measurement=measurement, angle=i * 360 / measurement_count)
                    for i, v in enumerate(r_mu_s)
                ]
            )
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
            self.measurement_manager.advance_motor(-int(round(phase_in_steps)))
            connections = [
                measurement.connection_1,
                measurement.connection_2,
                measurement.connection_3,
                measurement.connection_4,
            ]
            ra1, rb1 = measure_r_for_rs(self.measurement_manager, connections)
            self.measurement_manager.advance_motor(100)
            ra2, rb2 = measure_r_for_rs(self.measurement_manager, connections)
            ra = (ra1 + ra2) / 2
            rb = (rb1 + rb2) / 2
            print("the r's needed for rs:", ra, rb)

            f = lambda rs: np.exp(-pi * ra / rs) + np.exp(-pi * rb / rs) - 1
            df_drs = lambda rs: -(pi / rs ** 2) * (
                ra * np.exp(-pi * ra / rs) + rb * np.exp(-pi * rb / rs)
            )

            reasonable_rs_guess = (ra + rb) / 2
            rs = fsolve(f, reasonable_rs_guess, fprime=df_drs)[0]
            print("rs:", rs)
            mu = dr_db / rs
            print("mu:", mu)

            measurement.mobility = mu
            measurement.sheet_resistance = rs
            self.measurement_manager.end()


class RhValueView(viewsets.ModelViewSet):
    queryset = RhValue.objects.all()
    serializer_class = RhValueSerializer
    filter_class = RhValueFilter
    ordering = "-measurement_id"
