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
        self.measurement.open = False
        self.measurement.save()

    def setup_temperature_measurement(self):
        self.adc_manager.reset()
        self.adc_manager.offset_calibration()
        self.adc_manager.set_input_mode(InpmuxOptions.TEMP_SENS, InpmuxOptions.TEMP_SENS)

    def measure_temperature(self):
        value = self.adc_manager.read_value()
        TEMPERATURE_OFFSET = 25
        TEMPERATURE_OFFSET_VALUE = 0.1224
        TEMPERATURE_VOLT_PER_CELCIUS = 0.00042
        return (
            TEMPERATURE_OFFSET + (value - TEMPERATURE_OFFSET_VALUE) / TEMPERATURE_VOLT_PER_CELCIUS
        )

    def set_up_mobility_measurement(self):
        self.adc_manager.reset()
        self.adc_manager.enable_chop()
        self.adc_manager.set_reference_mode(ReferenceMode.SUPPLY, ReferenceMode.SUPPLY)
        self.adc_manager.start()

    def setup_current_measurement(self):
        self.adc_manager.set_input_mode(InpmuxOptions.AIN2, InpmuxOptions.AIN3)

    def setup_voltage_measurement(self):
        self.adc_manager.set_input_mode(InpmuxOptions.AIN0, InpmuxOptions.AIN1)

    def measure_voltage(self):
        return (self.adc_manager.read_value() * 10 - 2.5) / 100

    def measure_current(self):
        shunt_resistance = 9920
        return self.adc_manager.read_value() / shunt_resistance * 10

    def measure_current_and_voltage(self):
        self.setup_voltage_measurement()
        v = self.measure_voltage()
        self.setup_current_measurement()
        i = 10e-6  # used until we get this from the outside
        # i = self.measure_current()
        return v, i

    def advance_motor(self, steps):
        return  # tmp for test
        speed = min(10, abs(steps))
        self.motor_manager.turn(steps, micro_step=True, steps_per_second=speed)
