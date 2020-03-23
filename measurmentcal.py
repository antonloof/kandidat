#!/usr/bin/env python
# coding: utf-8

# In[10]:


import math
from numpy import diff
import numpy as np
import random
import matplotlib.pyplot as plt
# from sklearn.linear_model import LinearRegression

 # Defnintion av hitte-på funktioner. 
	
def move(n):
	return 

def measure():
	return random.randrange(0,100,1)*10^(-3)

i = 5*10^(-3); 

# Har här satt strömmen som en godtycklig variabel
# Kan vi mäta den ska vi såklart göra det istället.


# In[5]:


# Resistivitetsmätning
   
# Kolla att magneterna ligger rätt relativt provet. 
# Det jag utgått ifrån är att de börjar med att ligga så att det vinkelräta magnetfältet över provet är noll.
# Antog även att stegmotorn rör sig ett varv på 200 steg. Kan ha tagit fel på detta, då får vi ändra lite. 

V = measure()
r1 = V/i

move(100)

V= measure()
r2 = V/i

Rmnop = (r1+r2)/2

# Byt kontakter. 
# Kontakten som varit kopplad till in+ kopplas till jord.
# Kontakten som varit kopplad till in- kopplas till in+.
# Kontakten som varit kopplad till strömkällan kopplas till in-
# Kontakten som varit kopplad till jord kopplas till strömkällan. 

# in+ och in- beteckanar de två ingångarna till förstärkarsteget 
# Strömkällan och jord betecknar de kontakter som strömen skickas genom

V = measure()
r1 = V/i

move(100)

V= measure()
r2 = V/i

Rnopm = (r1+r2)/2

# Beräkning av Rs. Detta går möjligtvis att göra med en enkel python-funktion.
# Jag valde dock att göra det såhär eftersom det var enklare för mig, då jag är ny till python,
# Samt att jag nu har full kontroll över hur många noga min lösning är 
# Vi kan dock ändra detta om ni vet en bättre lösning, såklart.

def F(n, arg1 = Rmnop, arg2 = Rnopm):
   return math.exp(-math.pi * arg1 / n) + math.exp(-math.pi * arg2 /n)

def f(n, arg1 = Rmnop, arg2 = Rnopm):
   return math.exp(-math.pi * arg1 / n) + math.exp(-math.pi * arg2 /n) - 1

def derf(n, arg1 = Rmnop, arg2 = Rnopm): 
   return -math.pi*arg1 * math.exp(-math.pi * arg1 /n)/n - math.pi*arg2*math.exp(-math.pi*arg2/n)/n

x0 = 1
while F(x0) > 1.0001 or F(x0) < 0.9999:
   x0 += f(x0)/derf(x0)

Rs = x0

# In[13]:

# Laddningsbärarmobiliteten mu
	
b = 0.6  # Styrkan av magnetfältet.

R_mu = np.array([[]]) # Array för att spara mätvärden på R_mu
B = np.array([[]])	# Array för att spara mätvärden på B

n = 1
a = 20 # Antalet steg som stegmotorn tar mellan mätningarna 

# Mätcykeln dvs. Flytta, mät och spara värden. 
while n < 200:
	move(200/a)
	n += 200/a
	V = measure()
	R_mu = np.append([R_mu],V/i)
	Bb = math.cos(n*2*math.pi/200)*b
	B = np.append(B,Bb)
	
# Två olika sätt att beräkna mu, tror att linearregressions beräkningen ska vara bäst, 
# men är lite osäker om allt blev rätt. Slängde ihop det lite fort. 

# mu = Rs*(sum(diff(R_mu))/len(diff(R_mu)))/(sum(diff(B))/len(diff(B)))

B = B.reshape((-1, 1))
# model = LinearRegression().fit(B,R_mu)

# mu2 = Rs*model.coef_
