# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 11:16:06 2023

@author: laloa
"""
import numpy as np
from scipy.fft import fft,ifft
import scipy.interpolate as spi

def generate_grid(Power,Upper_lim):
    #Number of points in the grid, it must be a power of 2
    N = 2**Power
    #Imput the grid sizes for z 
    U = Upper_lim #Upper limit
    zini = -U
    zfin = U
    dz = (zfin-zini)/(N-1)
    zgrid = np.arange(zini, zfin +1e-10 , dz)
    
    #grid of x, but I need to take care of the relation dxdz = 2pi/N
    dx = (2*np.pi)/(N*dz)
    xini = -((N-1)/2)*dx
    xfin = -xini
    xgrid = np.arange(xini, xfin +1e-10 , dx)
    return [N,zini,zfin,dz,zgrid,dx,xini,xfin,xgrid]

def Call_Prices_Lewis(char_func, call_param, mod_param, grid = [] ):
    #the vector param must contain everything depending if the grid is given or not
    
    #Number of integration points
    if len(grid) == 0:
        r,T,F0,moneyness = call_param
        N,zini,zfin,dz,zgrid,dx,xini,xfin,xgrid = generate_grid(15,500)
        
    else:
        r,T,F0,moneyness = call_param
        N,zini,zfin,dz,zgrid,dx,xini,xfin,xgrid = grid
    
    #compute the vector z
    z = np.apply_along_axis(char_func, 0, zgrid,mod_param)*np.exp(-1j*xini*dz*np.arange(0,N,1))
    
    #Run the FFT on z
    zfft = fft(z)
    
    y = (dz*np.exp(-1j*zini*xgrid)*zfft).real
    
    I_mod = spi.splrep(xgrid,y,k=3)
    Int= spi.splev(moneyness,I_mod)
    
    #Value of the call options x = ln(K/F0) then K = exp(x)*F0 
    pricesfft = np.exp(-r*T)*F0*(1-np.exp(-moneyness/2)*Int/(2*np.pi))
    return pricesfft