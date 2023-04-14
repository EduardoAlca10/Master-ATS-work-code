# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 12:05:34 2023

@author: laloa
"""
#Changuing directory
import os
os.chdir('C:\\Users\\laloa\\OneDrive - Mälardalens högskola\\Master\\Master Thesis\\Code')
print(os.getcwd())

#Volatility shapes
import numpy as np
from Lewis_Pricing import *
from Black76_pricing import *
from Char_functions import *
import matplotlib.pyplot as plt

###################################################################################################
#Seting parameters

#Observed parameters
S0 = 100; r= .04; T = 1
F0 = S0*np.exp(r*T) #Forward price

#Model parameters
beta = 1; delta =-0.5   # power law scaling
sigma = 0.2; eta = 1 ; kappa = 1; alpha = 0.5

#Moneyness of our interest, FFT will give us the prices of this vector
moneyness = np.sqrt(T)*np.linspace(-0.2 , 0.2 , 9 )

#Obtaining strikes from defined moneyness
strikes = []
for j in range(len(moneyness)):
    strikes.append(np.asarray(np.exp(-moneyness[j]))*F0)
strikes = np.asarray(strikes)

###################################################################################################
#Seting parameters for the graphs
sigma = 0.2; eta = 1 ; kappa = 1
sigmas = [0.1,0.2,0.3]
etas = [.5,1,1.5]
kappas = [.5,1,1.5]

#Defining figures
plt.figure()

#Create graph with a for
colors =['r','g','b']
for sigma,color in zip(sigmas,colors): #Change parameters
    #Pricing Options
    pcall = [r,T,F0,moneyness]
    pmodel = [beta,delta,sigma,eta,kappa,alpha,T]
    prices = Call_Prices_Lewis(integrand,pcall,pmodel)
    #Calculating implied volatilities
    mod_imp_vol = []
    for j in range(len(moneyness)):
        call = call_option(F0, strikes[j], T, r, 0.15)
        mod_imp_vol.append(np.asarray(call.imp_vol(prices[j], 0.15)))
    mod_imp_vol = np.asarray(mod_imp_vol) 
    #Building the graphs
    #plt.plot(moneyness, prices,'g*')
    plt.plot(strikes, mod_imp_vol,color,marker = 'o', label='$\sigma$ = '+ str(sigma), ms = 3) #Change LABEL!!!
plt.grid(True)  # adds a grid
plt.xlim(85, 130)
#plt.ylim(.16, .22)                 ##ylim for ETA, KAPPA
plt.ylim(.05, .36)                  ##ylim for SIGMA
plt.ylabel("Implied Volatility")
plt.xlabel("Strike")
plt.legend(loc=0)
plt.show()