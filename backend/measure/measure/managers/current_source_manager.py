import pigpio
from time import sleep, time
from collections import namedtuple

EmitterResistance = namedtuple("EmitterResistance", ["pin", "re"])


class CurrentSourceManagerException(Exception):
    pass

TEMP_SENSOR_I2C_ADDRESS = 0x27
DAC_I2C_ADDRESS = 0b1100001
# pi.i2c_write_device(i2c, data) blir bra for att skriva till dacen

RES = [
    EmitterResistance(pin=4, re=1e3), 
    EmitterResistance(pin=17, re=1e4), 
    EmitterResistance(pin=27, re=1e5),
    EmitterResistance(pin=22, re=1e6)]
SATURATION_DETECT_PIN = 5

class CurrentSourceManager:
    def __init__(self, pi):
        self.pi = pi
        self.i2c = self.pi.i2c_open(1, TEMP_SENSOR_I2C_ADDRESS, 0)
        for re in RES:
            self.pi.set_mode(re.pin, pigpio.OUTPUT)
        self.write_re(RES[-1])
        self.pi.set_mode(SATURATION_DETECT_PIN, pigpio.INPUT)

    def close(self):
        self.pi.i2c_close(self.i2c)

    def is_saturated(self):
        return bool(self.pi.read(SATURATION_DETECT_PIN))
        
    def write_dac(self, value):
        pass
        
    def write_re(self, re):
        assert re in RES, f"{re} is not a valid emitter resistance"
        for re_a in RES:
            self.pi.write(re_a.pin, 0)
        self.pi.write(re.pin, 1)
        
    def read_temp_hum(self, timeout_s=3):
        # mat med HIH8120-021-001 (som alex var snall nog att ge till mig for att leka med)
        
        self.pi.i2c_write_quick(self.i2c, 0)
        status_bits = 0b11000000
        start = time()
        status = 1
        
        while status:
            (count, data) = self.pi.i2c_read_device(self.i2c, 4)
            if count < 0:
                print("error", data)
            status = (data[0] & status_bits) >> 6
            if time() - start > timeout_s:
                raise CurrentSourceManagerException("timeout")
                
            sleep(0.01)
            
        humidity = ((data[0] & (~status_bits)) << 8) + data[1]
        temp = (data[2] << 6) + ((data[3] & 0b11111100) >> 2)
        denominator = 2 ** 14 - 2

        return 165 * temp / denominator - 40, 100 * humidity / denominator
