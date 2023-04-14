# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 13:43:41 2023

@author: laloa
"""
#Changuing directory
import os
os.chdir('C:\\Users\\laloa\\OneDrive - Mälardalens högskola\\Master\\Master Thesis\\Code')
print(os.getcwd())

#Libraries
import pandas as pd
import numpy as np
import scipy.interpolate as spi
from Black76_pricing import *

###################################################################################
#Generate historical file with options

#Read options of the month
data = pd.read_csv("./Data_Master_thesis/ReferenceManual_raw_data/2020/OPT/INTL.IVYOPPRCD_201911.zip",sep = "	",header=0, compression='zip')
#Filter the information of interest [504880, 508313, 707860] = [EUROSTOXX,ABB,VIX]
filter0 = data["Currency"]== 814
filter1 = data["SecurityID"]== 504880
#Take columns of interest #Exchange 21 is EUREX
dataaux = data[["SecurityID","OptionID","Date","Exchange","Last","ImpliedVolatility"]][filter0 & filter1]#.set_index('OptionID')

#Read characteristics of all the options
data1 = pd.read_csv("./Data_Master_thesis/ReferenceManual_raw_data/2020/INTL.IVYOPHSTD.txt",sep = "	", header=0)
#data1.set_index('OptionID',inplace=True)
filter0 = data1["Currency"]== 814
filter1 = data1["CallPut"]== 'C'
filter2 = data["SecurityID"]== 504880
data1aux = data1[["OptionID","Strike","Expiration"]][filter0 & filter1 & filter2].drop_duplicates()

#Read Underlying prices
und = pd.read_csv("./Data_Master_thesis/ReferenceManual_raw_data/2020/Und/INTL.IVYSECPRD_201911.zip",sep = "	",header=0, compression='zip')
filter0 = und["Exchange"]== 21
filter1 = und["SecurityID"]== 504880
undaux = und[["Date","ClosePrice"]][filter0 & filter1]

#merge tables
dataaux = dataaux.merge(undaux,on = 'Date',how='left')

#Merge data frames
#info = prueba[prueba["Date"]== 20191101].merge(data1aux,on = 'OptionID')
info = dataaux.merge(data1aux,on = 'OptionID',how='left').dropna()

#Transform to date formats
info.dtypes
info['Date'] = pd.to_datetime(info['Date'], format='%Y%m%d')
info['Expiration'] = info['Expiration'].astype(int)
info['Expiration'] = pd.to_datetime(info['Expiration'], format='%Y%m%d')
info['Strike'] = info['Strike']/1000
info['DTM'] = info['Expiration']-info['Date']
info['DTM'] = info['DTM'].dt.days

#Cleaning
filter0 = info["DTM"] < 365*2
filter1 = info["ImpliedVolatility"] < .4
filter2 = info["ImpliedVolatility"] > 0
cleaninfo = info[filter0 & filter1 & filter2]


###################################################################################
#Generate historical file with the curves

#Months
months = ['201911', '201912', '202001', '202002', '202003', '202004',
       '202005', '202006', '202007', '202008', '202009', '202010','202011']

#Create data frame to put the rates
rates = pd.DataFrame()

#Join the files in one
for month in months:
    #Read file
    file = "C:/Users/laloa/OneDrive - Mälardalens högskola/Master/Master Thesis/Code/Data_Master_thesis/ReferenceManual_raw_data/2020/Curves/INTL.IVYZEROCD_" + str(month) + ".zip"
    rawrates = pd.read_csv(file, sep = "	", compression='zip', header=0)
    #Extract rates in EUR (814) and SEK (864)
    drates = rawrates.query("Currency in [814,864]")
    #Concatenate df
    rates = pd.concat([rates,drates],axis=0)

#reset index
rates.reset_index(inplace=True,drop=True)
#Path to save the file
path = "./Data_Master_thesis/ProcessedData/2020/MergedData/rates2020.csv"
#save file
rates.to_csv(path)

###################################################################################
#Generate historical file with dividends

#Months
months = ['201911', '201912', '202001', '202002', '202003', '202004',
       '202005', '202006', '202007', '202008', '202009', '202010','202011']

#Create data frame to put the rates
dividends = pd.DataFrame()

#Join the files in one
for month in months:
    #Read file
    file = "C:/Users/laloa/OneDrive - Mälardalens högskola/Master/Master Thesis/Code/Data_Master_thesis/ReferenceManual_raw_data/2020/Dvd/INTL.IVYIDXDVD_" + str(month) + ".zip"
    rawrates = pd.read_csv(file, sep = "	", compression='zip', header=0)
    #Extract dividend for the security 504880 (Eurostoxx)
    drates = rawrates.query("SecurityID in [504880]")
    drates = drates[drates["Rate"] > 0]
    #Concatenate df
    dividends = pd.concat([dividends,drates],axis=0)

#reset index
dividends.reset_index(inplace=True,drop=True)

#calculate the difference (Expiration-date) to be able to interpolate
dividends["Days"] = (pd.to_datetime(dividends["Expiration"],format='%Y%m%d') - pd.to_datetime(dividends["Date"],format='%Y%m%d')).dt.days
#Path to save the file
path = "./Data_Master_thesis/ProcessedData/2020/MergedData/dividends2020.csv"
#save file
dividends.to_csv(path)

###################################################################################
#Possible function to get data for one day
#read data
data = pd.read_pickle("./Data_Master_thesis/ProcessedData/2020/MergedData/dfestx.pkl")
zero_rates = pd.read_csv("./Data_Master_thesis/ProcessedData/2020/MergedData/rates2020.csv",index_col=0)

#get different dates
dates = data["Date"].unique()

#select a date
date = dates[0]

def obtain_info(date,data,zero_rates,div_curve):
    cond1 = data["Date"]==date
    #Get maturities for a given date
    aux_mat = np.asarray(data[cond1]["Tau"].unique())
    maturities = np.asarray(data[cond1]["Tau"].unique())/365
    
    #Get rates for the given maturities
    strdate = pd.to_datetime(date).strftime('%Y%m%d')
    filter1 = zero_rates["Currency"] == 864
    filter2 = zero_rates["Date"] == int(strdate)
    aux = zero_rates[filter1 & filter2][["Days","Rate"]]
    interpol = spi.splrep(np.asarray(aux["Days"]),np.asarray(aux["Rate"]),k=1)
    rates = spi.splev(aux_mat,interpol)
    
    #Get dividends rates for the given maturities
    filter1 = div_curve["Date"] == int(strdate)
    aux = div_curve[filter1][["Days","Rate"]]
    interpol = spi.splrep(np.asarray(aux["Days"]),np.asarray(aux["Rate"]),k=1)
    dividends = spi.splev(aux_mat,interpol)
    
    #Get Spot for a given date and calculate forward price
    spot = np.asarray(data[cond1]["spot"].unique())
    forwards = spot*np.exp((rates-dividends)*maturities)
    
    #Get Strikes for a given date
    v_strikes = []
    for mat in aux_mat:
        cond2 = data["Tau"] == mat
        v_strikes.append(np.asarray(data[cond1&cond2]["strike"]))
    v_strikes
    
    #calculate the moneyness np.exp(-v_moneyness[i][j])*forwards[i]
    v_moneyness = []
    for i in range(len(v_strikes)):
        aux = []
        for j in range(len(v_strikes[i])):
            aux.append(np.asarray(-np.log(v_strikes[i][j]/forwards[i])))
        v_moneyness.append(np.asarray(aux))
    
    #Get Implied volatility for a given date
    v_impl_vol = []
    for mat in aux_mat:
        cond2 = data["Tau"] == mat
        v_impl_vol.append(np.asarray(data[cond1&cond2]["impVol"]))
    v_impl_vol
    
    #Transform implied volatility to option prices
    v_mktprices = []
    for i in range(len(v_impl_vol)):
        aux_mp = []
        for j in range(len(v_impl_vol[i])):
            call = call_option(forwards[i], v_strikes[i][j], maturities[i], rates[i], v_impl_vol[i][j])
            aux_mp.append(call.value())
        v_mktprices.append(np.asarray(aux_mp))
    
    return maturities,rates,forwards,v_moneyness,v_strikes,v_mktprices,v_impl_vol



