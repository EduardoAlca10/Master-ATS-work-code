# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 20:52:25 2023

@author: laloa
"""

import numpy as np

#Definition of the characteristic functions

####################################################################################
#(Additive) Normal Tempered Stable Processes
def sub_lap_trans(u,p):
    kappa,alpha,T = p
    if alpha == 0:
        value = -(T/kappa)*np.log(1+u*kappa)
    else:
        value = (T/kappa)*((1-alpha)/alpha)*(1-(1+(u*kappa)/(1-alpha))**alpha)
    return np.exp(value)

def martingale_prop(p):
    sigma,eta,kappa,alpha,T = p
    par = [kappa,alpha,T]
    return -np.log(sub_lap_trans(sigma**2*eta,par))

def ATS_char(u,p):
    #read parameters
    beta,delta,sigma,eta,kappa,alpha,T = p
    kappa_t = kappa*T**beta
    eta_t = eta*T**delta
    
    #construct verctor for next functions
    p1 = [kappa_t,alpha,T]
    p2 = [sigma,eta_t,kappa_t,alpha,T]
    
    #aux variable for short expressions
    aux = 1j*u*(.5 + eta_t)*sigma**2 + .5*u**2*sigma**2
    return sub_lap_trans(aux,p1)*np.exp(1j*u*martingale_prop(p2))

def integrand(u,p):
    return ATS_char(-u-1j*.5,p)/(u**2+.25)

####################################################################################