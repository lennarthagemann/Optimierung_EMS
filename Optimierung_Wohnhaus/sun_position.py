# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 10:08:51 2022

@author: hagem
"""

import matplotlib.pyplot as plt
from Datenanalyse.Preprocessing_Functions import  pv
import numpy as np
from numpy.random import normal
filepath = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/BIblis_15minutes_power.csv'

Startdatum = '2022-08-20'
Enddatum = '2022-08-21'
pv_biblis = pv(filepath, Startdatum, Enddatum)

mu = 13*60+32
dist = 7*60+6

def raised_cosine(x, m, s):
    if x <= m+s and x >= m-s:
        return 1/(2*s)*(1 + np.cos(np.pi*(x - m)/s))
    else:
        return 0
    
values = [raised_cosine(x, mu, dist) for x in np.arange(1440)]
fig, axs = plt.subplots()
axs.plot(np.arange(1440), values)
plt.show()