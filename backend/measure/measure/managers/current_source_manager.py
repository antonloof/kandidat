import pigpio
from time import sleep, time
from collections import namedtuple
from enum import IntEnum

EmitterResistance = namedtuple("EmitterResistance", ["pin", "re"])
DacRead = namedtuple(
    "DacRead",
    ["ready", "power_down_reset", "active_power", "active_value", "eeprom_power", "eeprom_value"],
)


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
        self.pi.set_mode(SATURATION_DETECT_PIN, pigpio.INPUT)

    def begin(self):
        self.write_re(RES[-1])
        self.write_dac(OpCode.EEPROM, Power.OFF100K, 0)

    def end(self):
        self.write_dac(OpCode.NORMAL, Power.OFF100K, 0)

    def close(self):
        self.pi.i2c_close(self.i2c)

    def is_saturated(self):
        return not bool(self.pi.read(SATURATION_DETECT_PIN))

    def set_dac_value(self, value):
        self.write_dac(OpCode.NORMAL, Power.ON, value)

    def write_dac(self, opcode, power, value, timeout_s=1):
        assert power < 4, f"power cant be greater than 3, got {power}"
        assert value < 0x1000, f"Value must fit in 12 bits, got {value}"
        assert opcode in (2, 3), f"opcode must be one of 1,2,3, got {opcode}"

        if opcode == OpCode.EEPROM:
            dac_data = self.read_dac()
            if dac_data.eeprom_power == power and dac_data.eeprom_value == value:
                # expected config is written to dac, lets not waste eeprom write cycles
                opcode = OpCode.NORMAL

        data_opcode = opcode << 5
        data_power = power << 1
        data = [data_opcode + data_power, (value >> 4) & 0xFF, (value << 4) & 0xF0]
        self.pi.i2c_write_device(self.i2c, data * 2)

        if opcode == OpCode.EEPROM:
            dac_data = self.read_dac()
            start = time()
            while not dac_data.ready:
                dac_data = self.read_dac()
                if time() - start > timeout_s:
                    raise CurrentSourceManagerException(
                        f"write to eeprom timed out after {timeout_s}s"
                    )
                sleep(0.01)

    def read_dac(self):
        bytes_to_read = 5
        count, data = self.pi.i2c_read_device(self.i2c, bytes_to_read)
        if count != bytes_to_read:
            raise CurrentSourceManagerException(
                f"DAC read failed got {count} bytes expected {bytes_to_read}"
            )
        ready = bool(data[0] & 0x80)
        power_down_reset = bool(data[0] & 0x40)
        active_power = (data[0] >> 1) & 0b11
        active_value = (data[1] << 4) + (data[2] >> 4)
        eeprom_power = (data[3] >> 5) & 0b11
        eeprom_value = ((data[3] & 0b1111) << 8) + data[4]
        return DacRead(
            ready=ready,
            power_down_reset=power_down_reset,
            active_power=active_power,
            active_value=active_value,
            eeprom_power=eeprom_power,
            eeprom_value=eeprom_value,
        )

    def write_re(self, re):
        assert re in RES, f"{re} is not a valid emitter resistance"
        self.selected_re = re
        for re_a in RES:
            self.pi.write(re_a.pin, 0)
        self.pi.write(re.pin, 1)

    def set_current(self, current):
        min_c = VCC / 2 ** DAC_BITS / max(RES, key=lambda re: re.re).re
        max_c = VCC / min(RES, key=lambda re: re.re).re
        assert (
            min_c < current < max_c
        ), f"current must be between {min_c}A and {max_c}A got {current}"

        for re in reversed(RES):
            value = round(2 ** DAC_BITS * current * re.re / VCC)
            if 0 < value < 2 ** DAC_BITS:
                self.write_re(re)
                break
        self.set_dac_value(value)
