from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import pigpio


class SpiCommunication:
	def __init__(self):
		self.pi = pigpio.pi()
		self.spi = self.pi.spi_open(0, 48000, 0)
		print(self.spi)
	
	def write(self, bytes):
		self.pi.spi_write(self.spi, bytes)
		
	def read(self, count):
		c, d = self.pi.spi_read(self.spi, count)
		if c != count:
			raise RuntimeError(f"Got error from SPI read: tried to read {count} read: {c}. Data: {d}")
		return d
		
	def write_reg(self, addr, byte):
		opcode = [0x40 + addr, 1]
		self.write(opcode + [byte])
		
	def read_reg(self, addr):
		opcode = [0x20 + addr, 0]
		self.write(opcode)
		read = self.read(1)
		print(read)
		return read[0]

@require_POST
def measure(request):
	comm = SpiCommunication()
	comm.write_reg(0x04, 0x65)
	ret = comm.read_reg(0x04)
	return HttpResponse('{"id": ' + str(ret) + '}')

urlpatterns = [
	path('admin/', admin.site.urls),
	path('measure', measure),
]
