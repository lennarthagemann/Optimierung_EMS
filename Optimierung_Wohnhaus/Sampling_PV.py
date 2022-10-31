# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 09:13:11 2022

@author: hagem
"""
import matplotlib.pyplot as plt
from Datenanalyse.Preprocessing_Functions import dmd, prc, pv, car
import scipy.stats as st
import numpy as np
from numpy.random import normal
filepath = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/BIblis_15minutes_power.csv'

Startdatum = '2022-08-20'
Enddatum = '2022-08-21'
pv_biblis = pv(filepath, Startdatum, Enddatum)
pv_biblis_normed = pv_biblis/sum(pv_biblis)
x = np.linspace(-1,1,np.shape(pv_biblis)[0])
fig, axs = plt.subplots()
axs.plot(x, pv_biblis_normed)
mean = np.mean(pv_biblis)
std = np.std(pv_biblis)
