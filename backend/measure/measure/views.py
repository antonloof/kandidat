import pigpio

from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.http import require_POST
from time import sleep, time

from measure.models import Measurment


RESET_PIN = 26
START_PIN = 6
DATA_READY_PIN = 5
CS_PIN = 8


class SpiTimeoutException(Exception):
	pass


class SpiCommunication:
	def __init__(self):
		self.pi = None
		self.spi = None
		self.can_measure = False
		
		self.measurment = Measurment()
		open_measurments = Measurment.objects.select_for_update().filter(open=True)
		with transaction.atomic():
			self.can_measure = not open_measurments.exists()
			if self.can_measure:
				self.measurment.save()
				
	def __enter__(self):
		self.pi = pigpio.pi()
		self.spi = self.pi.spi_open(0, 50000, 1)
		self.pi.set_mode(START_PIN, pigpio.OUTPUT)
		self.pi.set_mode(RESET_PIN, pigpio.OUTPUT)
		self.pi.set_mode(DATA_READY_PIN, pigpio.INPUT)
		self.init()
		return self
		
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.pi.spi_close(self.spi)
		self.pi.stop()
		self.measurment.open = False
		self.measurment.save()
		
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
		self.pi.spi_write(self.spi, bytes)
		
	def read(self, count):
		c, d = self.pi.spi_read(self.spi, count)
		if c != count:
			raise RuntimeError(f"Got error from SPI read: tried to read {count} read: {c}. Data: {d}")
		return d
		
	def write_reg(self, addr, byte):
		opcode = [0x40 + addr, 0]
		self.write(opcode + [byte])
		
	def read_reg(self, addr):
		opcode = [0x20 + addr, 0]
		self.write(opcode)
		read = self.read(1)
		return read[0]
		
	def stop(self):
		self.pi.write(START_PIN, 0)
		sleep(0.1)
		
	def start(self):
		self.pi.write(START_PIN, 1)
		sleep(0.1)
		
	def init(self):
		self.reset()
		self.stop()
		self.reset_serial()
		self.start()
		
	def wait_for_data_ready(timeout_s=1):
		start = time()
		while pi.read(DATA_READY_PIN):
			sleep(0.001)
			if time() - start > timeout_s:
				raise SpiTimeoutException(f"wait_for_data_ready timed out after {timeout_s} seconds")

	def read_value(self, timeout_s=1):
		status = 0
		data = 0
		start_time = time()
		while not status & 0b01000000:
			self.wait_for_data_ready(timeout_s)
			pi.spi_write(spi, [0x12])
			c, data = pi.spi_read(spi, 6)
			if c != 6:
				print("error reading data, got to few bytes", c, "expected 6")
				continue
				
			status = data[0]
			checksum = (sum(data[1:5]) + 0x9B) & 0xFF
		
			if checksum != data[5]:
				print(f"checksum does not match. Got {data[5]} calculated {checksum}", data)
				
			sleep(0.0001)
			
			if time() - start_time > timeout_s:
				raise SpiTimeoutException(f"read_value timed out after {timeout_s} seconds")
			
		number = data[1] * 256**3 + data[2] * 256**2 + data[3] * 256**1 + data[4]
		if number & (1 << 31):
			number -= 1 << 32
		return 5*number/2**32


@require_POST
def start_measurement(request):
	c = SpiCommunication()
	if not c.can_measure:
		return HttpResponse('{"error": "another measurment is in progress. please wait a bit"}', status=400)
	
	with c as comm:
		comm.write_reg(0x04, 0x65)
		ret = comm.read_reg(0x04)
		return HttpResponse('{"id": ' + str(ret) + '}')
