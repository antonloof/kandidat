import pigpio

from django.db import transaction

from measure.models import Measurement
from measure.managers import *
from measure.filters import RhValueFilter


class MeasurementManager:
    def __init__(self, measurement_serializer):
        self.pi = None
        self.can_measure = False
        self.adc_manager = None
        self.motor_manager = None
        self.current_source_manager = None
        self.mux_manager = None

        open_measurements = Measurement.objects.select_for_update().filter(open=True)
        with transaction.atomic():
            self.can_measure = not open_measurements.exists()
            if self.can_measure:
                measurement_serializer.save()
        self.measurement = measurement_serializer.instance

    def begin(self):
        self.adc_manager.begin()
        self.motor_manager.begin()
        self.current_source_manager.begin()
        self.mux_manager.begin()

    def end(self):
        self.adc_manager.end()
        self.motor_manager.end()
        self.current_source_manager.end()
        self.mux_manager.end()

    def __enter__(self):
        self.pi = pigpio.pi()
        self.adc_manager = AdcManager(self.pi)
        self.motor_manager = MotorManager(self.pi)
        self.current_source_manager = CurrentSourceManager(self.pi)
        self.mux_manager = MuxManager(self.pi)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.adc_manager.close()
        self.motor_manager.close()
        self.current_source_manager.close()
        self.mux_manager.close()
        self.pi.stop()
        if exc_val:
            self.measurement.error = exc_val
        self.measurement.open = False
        self.measurement.save()

    def set_up_mobility_measurement(self):
        self.adc_manager.reset()
        # self.adc_manager.enable_chop()
        self.adc_manager.set_reference_mode(ReferenceMode.EXT0, ReferenceMode.EXT0)
        self.adc_manager.set_gain_data_rate(bypass=True)
        self.adc_manager.start()
        command = self.mux_manager.command()
        command.cp = self.measurement.connection_1
        command.cn = self.measurement.connection_3
        command.vp = self.measurement.connection_2
        command.vn = self.measurement.connection_4
        self.current_source_manager.set_current(self.measurement.current_limit)
        command.send()

    def setup_voltage_measurement(self):
        self.adc_manager.set_input_mode(InpmuxOptions.AIN8, InpmuxOptions.AIN9)

    def measure_voltage_calibration(self):
        return self.adc_manager.read_with_calibration() * 10 / 100

    def test_motor_current(self):
        shunt = 0.5  # WSR2R5000FEA
        max_current = 3  # A
        self.adc_manager.set_input_mode(InpmuxOptions.AIN4, InpmuxOptions.AIN1)
        current_a = abs(self.adc_manager.read_value() * 10 / shunt)
        self.adc_manager.set_input_mode(InpmuxOptions.AIN5, InpmuxOptions.AIN1)
        current_b = abs(self.adc_manager.read_value() * 10 / shunt)
        assert (
            current_a < max_current
        ), f"Too high current in the motor, something is broken. {current_a}A"
        assert (
            current_b < max_current
        ), f"Too high current in the motor, something is broken. {current_b}A"

    def measure_current_and_voltage(self):
        self.mux_manager.enable()
        self.setup_voltage_measurement()
        v = self.measure_voltage_calibration()
        i = self.current_source_manager.current
        self.mux_manager.disable()
        return v, i

    def advance_motor(self, steps, micro_step=True):
        steps_per_second = 20  # min(20, abs(steps))

        micro_multiplier = 2 if micro_step else 1
        for _ in range(abs(steps) * micro_multiplier):
            self.motor_manager.step(micro_step, sgn(steps))
            # self.test_motor_current()
            sleep(1 / (steps_per_second * micro_multiplier))
