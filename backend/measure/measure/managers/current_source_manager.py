import pigpio
from time import sleep

TEMP_SENSOR_I2C_ADDRESS = 0x27
DAC_I2C_ADDRESS = 0b1100000
# pi.i2c_write_device(i2c, data) blir bra for att skriva till dacen


class CurrentSourceManager:
    def __init__(self, pi, shift_register_manager):
        self.pi = pi
        self.i2c = self.pi.i2c_open(1, TEMP_SENSOR_I2C_ADDRESS, 0)

    def close(self):
        self.pi.i2c_close(self.i2c)

    def read_temp_hum(self):
        # mat med HIH8120-021-001 (som alex var snall nog att ge till mig for att leka med)
        (count, data) = self.pi.i2c_read_device(self.spi, 4)
        if count < 0:
            print("error", data)

        status_bits = 0b11000000
        status = (data[0] & status_bits) >> 6
        humidity = (data[0] & ~(status_bits) << 8) + data[1]
        temp = (data[2] << 6) + (data[3] & 0b11111100) >> 2

        denominator = 2 ** 14 - 2

        return 165 * temp / denominator - 40, 100 * humidity / denominator
