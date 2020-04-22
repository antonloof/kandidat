import pigpio
from time import sleep, time
from collections import namedtuple
from enum import IntEnum

EmitterResistance = namedtuple("EmitterResistance", ["pin", "re"])


class CurrentSourceManagerException(Exception):
    pass


class Power(IntEnum):
    ON = 0
    OFF1K = 1
    OFF100K = 2
    OFF500K = 3


class OpCode(IntEnum):
    NORMAL = 2
    EEPROM = 3

DAC_I2C_ADDRESS = 0b1100001

RES = [
    EmitterResistance(pin=15, re=1e3),
    EmitterResistance(pin=14, re=1e4),
    EmitterResistance(pin=23, re=1e5),
    EmitterResistance(pin=18, re=1e6),
]
SATURATION_DETECT_PIN = 4
VCC = 3.3
DAC_BITS = 12


class CurrentSourceManager:
    def __init__(self, pi):
        self.pi = pi
        self.i2c = self.pi.i2c_open(1, DAC_I2C_ADDRESS, 0)
        self.selected_re = None
        for re in RES:
            self.pi.set_mode(re.pin, pigpio.OUTPUT)
        self.write_re(RES[-1])
        self.pi.set_mode(SATURATION_DETECT_PIN, pigpio.INPUT)
        self.write_dac(OpCode.EEPROM, Power.OFF100K, 0)

    def close(self):
        self.write_dac(OpCode.NORMAL, Power.OFF100K, 0)
        self.pi.i2c_close(self.i2c)
        
    def is_saturated(self):
        return not bool(self.pi.read(SATURATION_DETECT_PIN))
        
    def set_dac_value(self, value):
        self.write_dac(OpCode.NORMAL, Power.ON, value)
        
    def write_dac(self, opcode, power, value):
        assert power < 4, f"power cant be greater than 3, got {power}"
        assert value < 0x1000, f"Value must fit in 12 bits, got {value}"
        assert opcode in (2, 3), f"opcode must be one of 1,2,3, got {opcode}" 
        
        opcode <<= 5
        power <<= 1
        data = [opcode + power, (value >> 4) & 0xFF, (value << 4) & 0xF0]
        #self.pi.i2c_write_device(self.i2c, data * 2)
        
    def write_re(self, re):
        assert re in RES, f"{re} is not a valid emitter resistance"
        self.selected_re = re
        for re_a in RES:
            self.pi.write(re_a.pin, 0)
        self.pi.write(re.pin, 1)
        
    def set_current(self, current):
        min_c = VCC / 2**DAC_BITS / max(RES, key=lambda re: re.re).re
        max_c = VCC / max(RES, key=lambda re: re.re).re
        assert min_c < current < max_c, f"current must be between {min_c}A and {max_c}A got {current}"
        
        for re in reversed(RES):
            if current * re.re < VCC:
                self.write_re(re)
                break
        value = round(2**DAC_BITS * current * self.selected_re.re / VCC)
        self.set_dac_value(value)
