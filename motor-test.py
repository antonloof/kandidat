
import pigpio
from time import sleep

# med en konstant (<200 och ganska låg) pwm fås att varrannat steg är längre/kortare, inte att föredra,
# men > 200 går fint
# nuvarande konf tror jag ger bättre än 100% alltid, men vet inte riktigt, hade varit nice att mäte lite
# när den börjar svänga... Med det kan vi nog konfa detta så det snurrar fint. Men vet om det e värt
# känns som en del jobb och en mekanisk dämpare duger kanske. 

pi = pigpio.pi()

a1 = 17
a2 = 27
b1 = 22
b2 = 26
powah = 10

pi.set_mode(a1, pigpio.OUTPUT)
pi.set_mode(a2, pigpio.OUTPUT)
pi.set_mode(b1, pigpio.OUTPUT)
pi.set_mode(b2, pigpio.OUTPUT)
pi.set_mode(powah, pigpio.OUTPUT)

pins = (a1, b1, a2, b2)
pi.write(powah, 1)
#pi.set_PWM_dutycycle(powah, 200)

steps = [
        (1,0,0,1),
       # (1,0,0,0),
        (1,1,0,0),
       # (0,1,0,0),
        (0,1,1,0),
      #  (0,0,1,0),
        (0,0,1,1),
      #  (0,0,0,1),
]
test = list(range(200, 230, 3)) + list(range(230, 255, 2))
step_count = 0
delay = 0.5
while step_count < 1000:
        for step in steps:
                for i, value in enumerate(step):
                        pi.write(pins[i], value)
                
                sleep(delay)
                step_count += 1

for p in pins:
	pi.write(p, 0)
pi.stop()

