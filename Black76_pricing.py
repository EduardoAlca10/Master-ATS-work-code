# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 11:43:51 2023

@author: laloa
"""

from math import log, sqrt, exp
from scipy import stats
from scipy.optimize import fsolve

class call_option(object):
    ''' Class for European call options in BSM Model.
    Attributes-
        F0: float         forward price
        K: float          strike price
        T: float       time to maturity
        r: float          constant risk-free short rate
        sigma: float      black volatility factor in diffusion term
    Methods-
        value: float      return present value of call option
        vega: float       return vega of call option
        imp_vol: float    return implied volatility given option quote'''
    
    def __init__(self, F0, K, T, r, sigma):
        self.F0 = float(F0)
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        
    def d1(self):
        ''' Helper function. '''
        d1 = (log(self.F0 / self.K) + 0.5 * self.sigma ** 2 * self.T) / (self.sigma * sqrt(self.T))
        return d1
    
    def value(self):
        ''' Return option value. '''
        d1 = self.d1()
        d2 = d1 - (self.sigma * sqrt(self.T))
        value = exp(-self.r * self.T)*(self.F0 * stats.norm.cdf(d1, 0.0, 1.0) - self.K * stats.norm.cdf(d2, 0.0, 1.0))
        return value
    
    def vega(self):
        ''' Return Vega of option. '''
        d1 = self.d1()
        vega = self.S0 * stats.norm.pdf(d1, 0.0, 1.0) * sqrt(self.T)
        return vega
    
    def imp_vol(self, C0, sigma_est=0.2):
        ''' Return implied volatility given option price. '''
        option = call_option(self.F0, self.K, self.T, self.r, sigma_est)
        def difference(sigma):
            option.sigma = sigma
            return option.value() - C0
        iv = fsolve(difference, sigma_est)[0]
        return iv