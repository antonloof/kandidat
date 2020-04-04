import pigpio
from time import sleep

A1_PIN = 12
A2_PIN = 16
B1_PIN = 20
B2_PIN = 21

STEP_SEQUENCE = (
	(1,0,0,1),
	(1,0,0,0),
	(1,1,0,0),
	(0,1,0,0),
	(0,1,1,0),
	(0,0,1,0),
	(0,0,1,1),
	(0,0,0,1),
)

def sgn(x):
	if x < 0:
		return -1
	if x > 0:
		return 1
	return 0

class MotorManager:
	def __init__(self, pi):
		self.pi = pi
		self.pins = (A1_PIN, B1_PIN, A2_PIN, B2_PIN)
		for pin in self.pins:
			pi.set_mode(pin, pigpio.OUTPUT)
		self.current_step = 0
		
	def close(self):
		for pin in self.pins:
			self.pi.write(pin, 0)
		
	def step(self, micro_step=False, direction=1):
		for i, value in enumerate(STEP_SEQUENCE[self.current_step]):
			self.pi.write(self.pins[i], value)
		self.current_step += direction * (1 if micro_step else 2)
		
		if self.current_step >= len(STEP_SEQUENCE):
			self.current_step -= len(STEP_SEQUENCE)
		if self.current_step < 0:
			self.current_step = len(STEP_SEQUENCE) - 1
		
	def turn(self, steps, micro_step=False, steps_per_second=10):
		# return # for testing
		micro_multiplier = 2 if micro_step else 1
		
		for _ in range(abs(steps) * micro_multiplier):
			self.step(micro_step, sgn(steps))
			sleep(1/(steps_per_second * micro_multiplier))
		
	
