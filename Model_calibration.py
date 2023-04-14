# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 19:26:04 2023

@author: laloa
"""

#Required libraries
#Main code
import numpy as np
from Lewis_Pricing import *
from Black76_pricing import *
from Char_functions import *
from scipy import optimize


###################################################################################################
#Model Calibration

#Definition of the error function
def error_function(p0,model_par, other_par):
    #Take parameters
    eta, sigma, kappa = p0
    beta,delta,alpha,grid = model_par
    maturities,rates,forwards,moneyness,mktprices = other_par 
    #note that maturities,rates,forward,moneyness must be vectors of the same lenght
    #moneyness and mktprices is a vector of vectors
    
    MSE_T = []
    #Price options
    for i in range(len(maturities)):
        pcall = [rates[i],maturities[i],forwards[i],moneyness[i]]
        pmodel = [beta,delta,sigma,eta,kappa,alpha,maturities[i]]
        model_values = Call_Prices_Lewis(integrand,pcall,pmodel,grid)
        market_values = mktprices[i]
        MSE_T.append(np.mean(((model_values - market_values) ** 2)))
        
    MSE = sum(MSE_T)/len(MSE_T)
    return MSE

#Perform calibration
def calibrate_model(fix_parameters,info):
    beta,delta,alpha = fix_parameters
    maturities,rates,forwards,v_moneyness,v_strikes,v_mktprices = info
    
    #Calculate grids for the FFT , the idea is to make the optimization faster
    grid = generate_grid(15,500)
    #Put together all the parameters needed for the calibration
    model_par = (beta,delta,alpha,grid)
    other_par = (maturities,rates,forwards,v_moneyness,v_mktprices)
    
    """
    #brute force WHY IT DOES NOT WORK???
    p0 = optimize.brute(error_function,
                ((0.5, 1.5, 0.01), # eta
                (0.01, .5, 0.1), # sigma
                (0.5, 1.5, 0.01)), # kappa
                args=(model_par,other_par),
                finish=None)
    """
    
    p0 = [1,.2,1]
    
    #second run with local, convex minimization WORKS PROPERLY
    optimal = optimize.fmin(error_function, p0, args=(model_par,other_par), xtol=0.000001, ftol=0.000001,maxiter=750, maxfun=900)
    optimal
    
    #second run with method ‘Nelder-Mead’ WORKS PROPERLY
    #optimal1 = optimize.minimize(error_function, [0,.2,1], args=(model_par,other_par), method = 'Nelder-Mead', tol=0.000001)
    #optimal1
    
    ###################################################################################################
    #Model prices and implied volatilies
    
    #Set optimal parameters
    eta,sigma,kappa = optimal
    
    #Repricing with the calibrated model and calculation of implied volatility
    v_mod_prices = [] 
    v_mod_imp_vol = []
    for i in range(len(maturities)):
        pcall = [rates[i],maturities[i],forwards[i],v_moneyness[i]]
        pmodel = [beta,delta,sigma,eta,kappa,alpha,maturities[i]]
        v_mod_prices.append(Call_Prices_Lewis(integrand,pcall,pmodel,grid))
        aux_iv = []
        for j in range(len(v_moneyness[i])):
            call = call_option(forwards[i], v_strikes[i][j], maturities[i], rates[i], 0.15)
            aux_iv.append(call.imp_vol(v_mod_prices[i][j], 0.15))
        v_mod_imp_vol.append(np.asarray(aux_iv))
    
    #Calculate implied volatility of the market prices
    v_mkt_imp_vol = []
    for i in range(len(v_mktprices)):
        aux_iv = []
        for j in range(len(v_mktprices[i])):
            call = call_option(forwards[i], v_strikes[i][j], maturities[i], rates[i], 0.15)
            aux_iv.append(call.imp_vol(v_mktprices[i][j], 0.15))
        v_mkt_imp_vol.append(np.asarray(aux_iv))
    
    return eta,sigma,kappa,v_mod_prices,v_mod_imp_vol,v_mkt_imp_vol