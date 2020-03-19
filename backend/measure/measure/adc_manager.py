from enum import IntEnum
import pigpio
from time import sleep, time

RESET_PIN = 26
START_PIN = 6
DATA_READY_PIN = 5
CS_PIN = 8


class Address(IntEnum):
	ID = 0
	POWER = 1
	INTERFACE = 2
	MODE0 = 3
	MODE1 = 4
	MODE2 = 5
	INPMUX = 6
	OFCAL0 = 7
	OFCAL1 = 8
	OFCAL2 = 9
	FSCAL0 = 10
	FSCAL1 = 11
	FSCAL2 = 12
	IDACMUX = 13
	IDACMAG = 14
	REFMUX = 15
	TDACP =  16
	TDACN = 17
	GPIOCON = 18
	GPIODIR = 19
	GPIODAT = 20
	
class OpCode(IntEnum):
	NOP = 0
	RESET = 0x06
	START1 = 0x08
	STOP1 = 0x0A
	RDATA1 = 0x12
	SYOCAL1 = 0x16
	SYGCAL1 = 0x17
	SFOCAL1 = 0x19
	READ = 0x20
	WRITE = 0x40

class StatusBit(IntEnum):
	ADC2 =     0b10000000
	ADC1 =     0b01000000
	EXTCLK =   0b00100000
	REF_ALM =  0b00010000
	PGAL_ALM = 0b00001000
	PGAH_ALM = 0b00000100
	PGAD_ALM = 0b00000010
	RESET    = 0b00000001
	
class Mode0Bbit(IntEnum):
	REFREV =        0b10000000
	RUNMODE =       0b01000000
	IDAC_ROTATION = 0b00100000
	INPUT_CHOP =    0b00010000
	DELAY3 =        0b00001000
	DELAY2 =        0b00000100
	DELAY1 =        0b00000010
	DELAY0 =        0b00000001
	
class InpmuxOptions(IntEnum):
	AIN0 = 0
	AIN1 = 1
	AIN2 = 2
	AIN3 = 3
	AIN4 = 4
	AIN5 = 5
	AIN6 = 6
	AIN7 = 7
	AIN8 = 8
	AIN9 = 9
	AINCOM = 10
	TEMP_SENS = 11
	AN_POWER = 12
	DIG_POWER = 13
	TDAC = 14
	FLOAT = 15
	
class Gain(IntEnum):
	G1 = 0
	G2 = 1
	G4 = 2
	G8 = 3
	G16 = 4
	G32 = 5
	
class DataRate(IntEnum):
	SPS2D5 = 0
	SPS25 = 1
	SPS10 = 2
	SPS16D6 = 3
	SPS20 = 4
	SPS50 = 5
	SPS60 = 6
	SPS100 = 7
	SPS400 = 8
	SPS1200 = 9
	SPS2400 = 10
	SPS4800 = 11
	SPS7200 = 12
	SPS14400 = 13
	SPS19200 = 14
	SPS38400 = 15

	
	
class AdcRuntimeException(Exception):
	pass
	
class AdcTimeoutException(AdcRuntimeException):
	pass

	
class AdcManager:
	def __init__(self, pi):
		self.pi = pi
		self.spi = pi.spi_open(0, 50000, 1)
		
		self.pi.set_mode(START_PIN, pigpio.OUTPUT)
		self.pi.set_mode(RESET_PIN, pigpio.OUTPUT)
		self.pi.set_mode(DATA_READY_PIN, pigpio.INPUT)
		
		self.reset()
		self.stop()
		self.reset_serial()
		self.start()

	def close(self):
		self.pi.spi_close(self.spi)

	def reset(self):
		self.pi.write(RESET_PIN, 1)
		sleep(0.1)
		self.pi.write(RESET_PIN, 0)
		sleep(0.1)
		self.pi.write(RESET_PIN, 1)
		sleep(0.1)
	
	def reset_serial(self):
		self.pi.write(CS_PIN, 1)
		sleep(0.1)
		self.pi.write(CS_PIN, 0)
		sleep(0.1)

	def write(self, bytes):
		if not isinstance(bytes, list):
			bytes = [bytes]
		self.pi.spi_write(self.spi, bytes)
		
	def read(self, count):
		c, d = self.pi.spi_read(self.spi, count)
		if c != count:
			raise AdcRuntimeException(f"Got error from SPI read: tried to read {count} read: {c}. Data: {d}")
		return d
		
	def write_reg(self, addr, byte):
		opcode = [OpCode.WRITE + addr, 0]
		self.write(opcode + [byte])
		
	def read_reg(self, addr):
		opcode = [OpCode.READ + addr, 0]
		self.write(opcode)
		read = self.read(1)
		return read[0]
		
	def stop(self):
		self.pi.write(START_PIN, 0)
		sleep(0.1)
		
	def start(self):
		self.pi.write(START_PIN, 1)
		sleep(0.1)
				
	def wait_for_data_ready(self, timeout_s=1):
		start = time()
		while self.pi.read(DATA_READY_PIN):
			sleep(0.001)
			if time() - start > timeout_s:
				raise AdcTimeoutException(f"wait_for_data_ready timed out after {timeout_s} seconds")
			
	def read_value(self, timeout_s=1):
		status = 0
		value_bytes = None
		start_time = time()
		
		while not status & StatusBit.ADC1:
			self.wait_for_data_ready(timeout_s)
			self.write(OpCode.RDATA1)
			data = self.read(6)	
			status = data[0]
			
			value_bytes = data[1:5]
			if not validate_checksum(value_bytes, data[5]):
				raise AdcRuntimeException(f"checksum does not match.", list(map(int, data)))
				
			sleep(0.0001)
			if time() - start_time > timeout_s:
				raise AdcTimeoutException(f"read_value timed out after {timeout_s} seconds")
					
		return 5*two_complement_to_float(value_bytes)
				
	def set_input_mode(self, positive, negative):
		self.write_reg(Address.INPMUX, (positive << 4) | negative)
		
	def offset_calibration(self):
		# disable chopmode, set to free running
		# set all inputs floating
		# run calibration
		# enable chop mode if it was before
		# restore previous input config
		self.stop()
		current_mode0 = self.read_reg(Address.MODE0)
		current_inpmux = self.read_reg(Address.INPMUX)
		self.write_reg(Address.MODE0, current_mode0 & ~(Mode0Bbit.RUNMODE & Mode0Bbit.INPUT_CHOP & Mode0Bbit.IDAC_ROTATION))
		self.set_input_mode(InpmuxOptions.FLOAT, InpmuxOptions.FLOAT)
		self.start()
		self.write(OpCode.SFOCAL1)
		self.wait_for_data_ready()
		self.write_reg(Address.MODE0, current_mode0)
		self.write_reg(Address.INPMUX, current_inpmux)
		
	def set_gain_data_rate(gain=Gain.G1, data_rate=DataRate.SPS20, bypass=False):
		bypass_bit = 0b10000000 if bypass else 0
		self.write_reg(Address.MODE2, bypass_bit | (gain << 4) | data_rate)

	def enable_chop(self):
		mode0 = self.read_reg(Address.MODE0)
		self.write_reg(Address.MODE0, mode0 | Mode0Bbit.INPUT_CHOP)

def validate_checksum(values, checksum):
	checksum_base = 0x9B
	return (sum(values) + checksum_base) & 0xFF == checksum

	
def two_complement_to_float(bytes):
	total = 0
	for byte in bytes:
		total <<= 8
		total += byte
	no_bits = 8 * len(bytes)
	if total & (1 << (no_bits - 1)):
		total -= 1 << no_bits
	return total/(1 << no_bits)