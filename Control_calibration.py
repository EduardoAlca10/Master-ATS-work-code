# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 11:28:38 2023

@author: laloa
"""

#Changuing directory
import os
os.chdir('C:\\Users\\laloa\\OneDrive - Mälardalens högskola\\Master\\Master Thesis\\Code')
print(os.getcwd())

#Main code
from Lewis_Pricing import *
from Black76_pricing import *
from Char_functions import *
from Model_calibration import *
from Mkt_Data_EUREX import get_info
from Control_data import obtain_info
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

###################################################################################################
#Simple example with some values to see easy results

#Observed parameters
S0 = 100; r= .04; T = 1/12
F0 = S0*np.exp(r*T) #Forward price

#Model parameters
beta = 1; delta =-0.5   # power law scaling
sigma = 0.2; eta = 1 ; kappa = 1; alpha = 0.5

#Moneyness of our interest, FFT will give us the prices of this vector
moneyness = np.sqrt(T)*np.linspace(-0.2 , 0.2 , 9 )

#Pricing Options
pcall = [r,T,F0,moneyness]
pmodel = [beta,delta,sigma,eta,kappa,alpha,T]
prices = Call_Prices_Lewis(integrand,pcall,pmodel)
prices
plt.plot(moneyness, prices,'g*')

####################################
#Data for the calibration (TEST)

#Simple test
maturities = [T]
rates = [r]
forwards = [F0]
v_moneyness = [moneyness] #x = ln(K/F0) then K = exp(x)*F0
v_mktprices = [prices]
v_strikes = []
for i in range(len(v_moneyness)):
    aux = []
    for j in range(len(v_moneyness[i])):
        aux.append(np.asarray(np.exp(-v_moneyness[i][j]))*forwards[i])
    v_strikes.append(np.asarray(aux))


###################################################################################################
#Data for the calibration info Bloomberg as of 21-03-2023
v_mktprices =[[53.9,65,77.3,90.65,105.05,120.7,137.15,154.4,172]
              ,[62.4,72.65,83.6,95.85,108.75,122.45,136.95,152.15,168.05]
              ,[83.85,94.85,106.35,118.6,131.65,145.35,159.75,174.65,190.2]
              ,[112.15,123.8,134.95,148.45,161.85,175.95,190.6,205.1,221.45]
              ,[132.95,144.65,157.75,170.95,184.75,199,213.7,228.9,244.5]
              ,[154.35,166.8,179.7,193.2,207.1,220.95,236.3,251.45,267.1]
              ,[177.4,190.65,203.8,217.3,231.2,245.65,260.6,275.85,291.5]
              ,[196.1,208.6,222.25,236.05,250.15,264.2,279.45,294.65,310.3]
              ,[211.3,224.3,237.7,251.5,265.7,280.2,295,310.2,325.7]]
for i in range(len(v_mktprices)): 
    v_mktprices[i] = np.asarray(v_mktprices[i])

maturities = np.asarray([31,59,87,122,150,178,213,241,269])/365
rates = np.asarray([3.02,3.02,3.02,3.02,3.02,3.02,3.28,3.37,3.44])/100
forwards = np.asarray([4180.62,4129.42,4123.62,4129.86,4135.60,4144.83,4153.25,4159.78,4165.68])
v_strikes= [np.asarray([4275,4250,4225,4200,4175,4150,4125,4100,4075])]*len(v_mktprices)

v_moneyness = []
for i in range(len(v_strikes)):
    aux = []
    for j in range(len(v_strikes[i])):
        aux.append(np.asarray(-np.log(v_strikes[i][j]/forwards[i])))
    v_moneyness.append(np.asarray(aux))

###################################################################################################
#Data for the calibration info EUREX
months = [4,5,6,7,8,9,10,11,12,1]
years = [2023,2023,2023,2023,2023,2023,2023,2023,2023,2024]
typeopt = "Call" #we can also write "Put"
val_date = datetime.date(2023, 3, 22) #Date of the market data

maturities_d,v_mktprices_p,v_strikes,spot = get_info(val_date,months,years,"Put")    
maturities_d,v_mktprices,v_strikes,spot = get_info(val_date,months,years,typeopt)

#https://www.suomenpankki.fi/en/Statistics/interest-rates/charts/korot_kuviot/euriborkorot_pv_chrt_en/
hist_rates = pd.read_csv("./EUR_rates.csv",index_col=0)
hist_rates.index = pd.to_datetime(hist_rates.index)
y = np.asarray(hist_rates.loc[val_date])
x = np.asarray([7,30,90,180,360])
interpol = spi.splrep(x,y,k=1)
rates = spi.splev(maturities_d,interpol)/100

maturities = maturities_d/365

forwards = []
for p in range(len(maturities)):
    forwards.append((((v_mktprices[p] - v_mktprices_p[p]))*np.exp(rates[p]*maturities[p]) + v_strikes[p])[int(len(maturities)/2)])

v_moneyness = []
for i in range(len(v_strikes)):
    aux = []
    for j in range(len(v_strikes[i])):
        aux.append(np.asarray(-np.log(v_strikes[i][j]/forwards[i])))
    v_moneyness.append(np.asarray(aux))

#Set fix parameters of the model
beta = 1; delta = -0.5; alpha = 0.5
#beta = 0; delta = 0; alpha = 0.5

info = [maturities,rates,forwards,v_moneyness,v_strikes,v_mktprices]
fix_parameters = [beta,delta,alpha]

eta,sigma,kappa,v_mod_prices,v_mod_imp_vol,v_mkt_imp_vol = calibrate_model(fix_parameters,info)
eta,sigma,kappa

###################################################################################################
#Data for the calibration info given by the supervisor

#read data
data = pd.read_pickle("./Data_Master_thesis/ProcessedData/2020/MergedData/dfestx.pkl")
zero_rates = pd.read_csv("./Data_Master_thesis/ProcessedData/2020/MergedData/rates2020.csv",index_col=0)
div_curve = pd.read_csv("./Data_Master_thesis/ProcessedData/2020/MergedData/dividends2020.csv",index_col=0)

#get different dates
dates = data["Date"].unique()

#select a date
date = dates[0]

#obtain all the information for a single date
maturities,rates,forwards,v_moneyness,v_strikes,v_mktprices,v_mkt_imp_vol = obtain_info(date,data,zero_rates,div_curve)
#maturities = maturities[[0,1,2,3,5,6,7,8]]

#Boundaries in moneyness
for j in range(len(maturities)):
    vector = (v_moneyness[j] < 0.12*np.sqrt(maturities[j])) & (v_moneyness[j] > -0.12*np.sqrt(maturities[j]))
    v_moneyness[j] = v_moneyness[j][vector]
    v_strikes[j] = v_strikes[j][vector]
    v_mktprices[j] = v_mktprices[j][vector]
    v_mkt_imp_vol[j] = v_mkt_imp_vol[j][vector]    

for j in range(len(maturities)):
    vector = (v_moneyness[j] < 0.12*np.sqrt(maturities[j])) & (v_moneyness[j] > -0.12*np.sqrt(maturities[j]))
    print(len(v_moneyness[j][vector]),len(v_moneyness[j]))

#Set fix parameters of the model
beta = 1; delta = -0.5; alpha = 0.5
#beta = 0; delta = 0; alpha = 0.5

info = [maturities,rates,forwards,v_moneyness,v_strikes,v_mktprices]
fix_parameters = [beta,delta,alpha]

eta,sigma,kappa,v_mod_prices,v_mod_imp_vol,v_mkt_imp_vol = calibrate_model(fix_parameters,info)
eta,sigma,kappa

###################################################################################################
#Graphs

i = 8
#Plot with Implied Volatilities
plt.figure()
plt.plot(v_strikes[i],v_mkt_imp_vol[i],'ro',label="Mkt")
plt.plot(v_strikes[i],v_mod_imp_vol[i],label="Mod",color ='c')
plt.grid(True)
plt.ylabel("Implied Volatility")
plt.xlabel("Strike")
plt.legend(loc=0)
#plt.ylim(.13, .2)
plt.title('Maturity: Dec-23')
plt.show()

#Plot with Option Prices
plt.figure()
plt.plot(v_strikes[i],v_mktprices[i],label="Mkt")
plt.plot(v_strikes[i],v_mod_prices[i],label="Mod")
plt.grid(True)
plt.ylabel("Call Prices")
plt.xlabel("Strike")
plt.legend(loc=0)
plt.show()

#Plot with Implied Volatilities
plt.figure()
plt.plot(v_moneyness[i],v_mkt_imp_vol[i],label="Mkt")
plt.plot(v_moneyness[i],v_mod_imp_vol[i],label="Mod")
plt.grid(True)
plt.ylabel("Implied Volatility")
plt.xlabel("Strike")
plt.legend(loc=0)
#plt.ylim(.13, .2)
plt.show()

#Diferent maturities in same graph
mat = [1,3,6,8]
colors = ["g","r","b","c"]
plt.figure()
for i,col in zip(mat,colors):
    plt.plot(v_strikes[i],v_mkt_imp_vol[i],color=col)
    plt.plot(v_strikes[i],v_mod_imp_vol[i], 'ro',label=i,color=col)
plt.grid(True)
plt.ylabel("Implied Volatility")
plt.xlabel("Strike")
plt.legend(loc=0)
#plt.ylim(.13, .2)
plt.show()



[4,5,6,7,8,9,10,11,12,1]
mat = [1,3,6,8]
matlabel = ['May-23','Jul-23','Oct-23','Dec-23']
colors = ["g","r","b","c"]
plt.figure()
for i,col,lab in zip(mat,colors,matlabel):
    plt.plot(v_strikes[i],v_mktprices[i],color=col)
    plt.plot(v_strikes[i],v_mod_prices[i], 'ro',label=lab,color=col)
plt.grid(True)
plt.ylabel("Call Prices")
plt.xlabel("Strike")
plt.legend(loc=0)
plt.title('Information as of 22-Mar-2023')
plt.show()

