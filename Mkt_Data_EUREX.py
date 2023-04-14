# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 18:24:56 2023

@author: laloa
"""
#Required libraries
import datetime
import pandas as pd
import numpy as np
import requests
from requests_html import HTMLSession
import calendar

############################################################################################
#Definition of our market data using webscraping methods over the webpage www.eurex.com
#https://www.eurex.com/ex-en/data/statistics/market-statistics-online/100!onlineStats?productGroupId=13370&productId=69660&viewType=3&cp=Call&year=2023&month=06&busDate=20230315

#write by hand the months and the years you want to consider for the calibration
#the code will take the pair of elements, por example, the firt maturity that will be considered is: January 2023
months = [4,7,10,1,4,12]
years = [2023,2023,2023,2024,2024,2024]
typeopt = "Call" #we can also write "Put"
val_date = datetime.date(2023, 3, 21) #Date of the market data

#The maturity of these options is the third friday of the month
def third_friday(year,month):
    '''This formula calculate the third friday of the given year and month
    Parameters-
        year: int
        month: int
    Returns-
        fri: date   third friday
    '''
    c = calendar.Calendar(firstweekday=calendar.SATURDAY)
    fri = c.monthdatescalendar(year, month)[2][6]
    return fri

def get_info(val_date,months,years,typeopt="Call"):
    #Get Stock price
    link1 = "https://www.eurex.com/ex-en/data/statistics/market-statistics-online/100!onlineStats?productGroupId=13370&productId=69660&viewType=3&"
    auxl = str(val_date.year)+val_date.strftime('%m')+val_date.strftime('%d')
    auxm = str(months[0]).zfill(2)
    link2 = "cp="+ typeopt + "&year="+str(years[0])+"&month="+auxm+"&busDate="+auxl
    url= link1 + link2
    
    session = HTMLSession()
    r = session.get(url)
    S0 = r.html.find('dd')[5].text
    S0 = float(S0.replace(",",""))
    
    #Get option prices
    options = pd.DataFrame()
    v_mktprices = []
    v_strikes = []
    maturities = []
    spot = np.asarray([S0]*len(months))
    
    #Write "percentage" if you want the options that deviates from the ATM certain toletance percentage
    criteria = "other" #we can also write "percentage"
    tol = 0.02
    
    for m,y in zip(months,years):
        link1 = "https://www.eurex.com/ex-en/data/statistics/market-statistics-online/100!onlineStats?productGroupId=13370&productId=69660&viewType=3&"
        auxl = str(val_date.year)+val_date.strftime('%m')+val_date.strftime('%d')
        auxm = str(m).zfill(2)
        link2 = "cp="+ typeopt + "&year="+str(y)+"&month="+auxm+"&busDate="+auxl
        url= link1 + link2
        
        #Get df with option prices
        r = requests.get(url)
        df = pd.read_html(r.text)[0]
        df.drop(df.tail(1).index,inplace=True)
        #Aux to filter what I want
        #Get #"Daily settlem. price" or "Last price"
        prueba = df.loc[:,["Strike price","Daily settlem. price"]].copy() 
        prueba['Strike price'] = prueba['Strike price'].astype(float)
        cond = (prueba["Daily settlem. price"] != 0) & (prueba['Strike price']%25 == 0)
        prueba = prueba[cond].copy()
        if criteria == "percentage":
            prueba = prueba[(np.abs(prueba['Strike price'] - S0) / S0) < tol].copy()
        else:
            prueba.reset_index(inplace = True, drop = True)
            ind = prueba[prueba['Strike price']==round(S0, -2)].index.values.astype(int)[0]
            #prueba = prueba.iloc[ind-5:ind+4].copy()
            prueba = prueba.iloc[ind-7:ind+6].copy()
        
        prueba['Maturity'] =  third_friday(y,m)
        prueba['Date'] =  val_date
        maturities.append((third_friday(y,m) - val_date).days)
        v_mktprices.append(np.flip(np.asarray(prueba["Daily settlem. price"])))
        v_strikes.append(np.flip(np.asarray(prueba['Strike price'])))
        
        options = pd.concat([options, prueba], axis=0) 
        
    options.reset_index(inplace = True, drop = True)   
    return np.asarray(maturities),v_mktprices,v_strikes,spot
    
