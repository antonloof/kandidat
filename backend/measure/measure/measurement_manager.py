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
        self.adc_manager.enable_chop()
        self.adc_manager.set_reference_mode(ReferenceMode.EXT0, ReferenceMode.SUPPLY)
        self.adc_manager.start()
        command = self.mux_manager.command()
        command.cp = self.measurement.connection_1
        command.cn = self.measurement.connection_3
        command.vp = self.measurement.connection_2
        command.vn = self.measurement.connection_4
        command.send()
        self.current_source_manager.set_current(self.measurement.current_limit * 1e10)

    def setup_current_measurement(self):
        self.adc_manager.set_input_mode(InpmuxOptions.AIN2, InpmuxOptions.AIN3)

    def setup_voltage_measurement(self):
        self.adc_manager.set_input_mode(InpmuxOptions.AIN8, InpmuxOptions.AIN1)

    def measure_voltage_calibration(self):
        return format_voltage(self.adc_manager.read_with_calibration())

    def test_motor_current(self):
        shunt = 0.5  # WSR2R5000FEA
        max_current = 3  # A
        self.adc_manager.set_input_mode(InpmuxOptions.AIN4, InpmuxOptions.AIN1)
        current_a = abs(self.adc_manager.read_value() * 10 / shunt)
        self.adc_manager.set_input_mode(InpmuxOptions.AIN5, InpmuxOptions.AIN1)
        current_b = abs(self.adc_manager.read_value() * 10 / shunt)
        print(current_a, current_b)
        assert (
            current_a < max_current
        ), f"Too high current in the motor, something is broken. {current_a}A"
        assert (
            current_b < max_current
        ), f"Too high current in the motor, something is broken. {current_b}A"

    def measure_voltage(self):
        v1 = format_voltage(self.adc_manager.read_value())
        self.mux_manager.swap_voltage()
        v2 = format_voltage(self.adc_manager.read_value())
        return (v1 + v2) / 2

    def measure_current(self):
        shunt_resistance = self.current_source_manager.selected_re.re
        return self.adc_manager.read_value() / shunt_resistance * 10

    def measure_current_and_voltage(self):
        self.setup_voltage_measurement()
        v = self.measure_voltage_mux_chop()
        # v = self.measure_voltage_calibration()
        self.setup_current_measurement()
        i = self.measure_current()
        return v, i

    def advance_motor(self, steps):
        speed = min(10, abs(steps))
        self.test_motor_current()
        self.motor_manager.turn(steps, micro_step=True, steps_per_second=speed)


def format_voltage(value):
    return (value * 10 - 2.5) / 100
