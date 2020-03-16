import pigpio
from time import sleep
pi = pigpio.pi()
spi = pi.spi_open(0, 50000, 1)

RESET_PIN = 26
START_PIN = 6
DATA_READY_PIN = 5
CS_PIN = 8

def reset():
	pi.write(RESET_PIN, 1)
	sleep(0.1)
	pi.write(RESET_PIN, 0)
	sleep(0.1)
	pi.write(RESET_PIN, 1)
	sleep(0.1)

def stop():
	pi.write(START_PIN, 0)
	sleep(0.1)

def reset_serial():
	pi.write(CS_PIN, 1)
	sleep(0.1)
	pi.write(CS_PIN, 0)
	sleep(0.1)

def init_adc():
	pi.set_mode(START_PIN, pigpio.OUTPUT)
	pi.set_mode(RESET_PIN, pigpio.OUTPUT)
	pi.set_mode(DATA_READY_PIN, pigpio.INPUT)
	reset()
	stop()
	reset_serial()
	start()

def read_reg(addr):
	data = [0x20 | addr, 0]
	pi.spi_write(spi, data)
	c, data = pi.spi_read(spi, 1)
	if c != 1:
		print("error reading spi")
	return data[0]

def write_reg(addr, byte):
	data = [0x40 | addr, 0, byte] 
	pi.spi_write(spi, data)
	read = read_reg(addr)
	if read != byte:
		print(f"error writing data. Tried to write {byte} but read {read}")
	

def start():
	pi.write(START_PIN, 1)
	sleep(0.1)


def wait_for_data_ready():
	while pi.read(DATA_READY_PIN):
		sleep(0.001)

def read_value():
	status = 0
	data = 0
	while not status & 0b01000000:
		wait_for_data_ready()
		pi.spi_write(spi, [0x12])
		c, data = pi.spi_read(spi, 6)
		if c != 6:
			print("error reading data, got to few bytes", c, "expected 6")
		status = data[0]
		checksum = (sum(data[1:5]) + 0x9B) & 0xFF
	
		if checksum != data[5]:
			print(f"checksum does not match. Got {data[5]} calculated {checksum}", data)
<<<<<<< HEAD
		sleep(0.0001)

	number = data[1] * 256**3 + data[2] * 256**2 + data[3] * 256**1 + data[4]
	if number & (1 << 31):
		number -= 1 << 32
	return 5*number/2**32

def offset_calibration():
	# disable chopmode, set to free running
	# set all inputs floaating
	# run calibration
	# enable chop mode if it was before
	stop()
	current_mode0 = read_reg(3)
	current_inpmux = read_reg(6)
	write_reg(3, current_mode0 & 0b10001111)
	write_reg(6, 0xFF)
	
	start()
	pi.spi_write(spi, [0x19])
	wait_for_data_ready()
	write_reg(3, current_mode0)
	write_reg(6, current_inpmux)

init_adc()
write_reg(1, 0b00000011)
write_reg(2, 0b00000101)
write_reg(3, 0b00000000)
write_reg(4, 0b01100000)
write_reg(5, 0b00000110)
write_reg(6, 0b10111011) # measure temp
offset_calibration()
print(25 + (read_value() - 0.1224)/0.00042, "celsius")
stop()
write_reg(3, 0b00010000) # enable chop mode, cant be on when measureing temp
write_reg(6, 0b00000001)
start()

for i in range(100):
	print(read_value() * 1000)
=======
		sleep(0.010)

	number = data[1] * 256**3 + data[2] * 256**2 + data[3] * 256**1 + data[4]
	return 5*number/2**32

init_adc()
write_reg(1, 0b00000001)
write_reg(2, 0b00000101)
write_reg(3, 0b00000000)
write_reg(4, 0b10000000)
write_reg(5, 0b10010010)
write_reg(6, 0b10111011) # measure temp
print(25 + (read_value() - 0.1224)/0.00042, "celsius")

stop()
write_reg(6, 0b00000001)
start()
for i in range(100):
	print(read_value())
>>>>>>> f323700f1c09f87f1e8adbdd741a8b899ca98467

pi.spi_close(spi)
pi.stop()
