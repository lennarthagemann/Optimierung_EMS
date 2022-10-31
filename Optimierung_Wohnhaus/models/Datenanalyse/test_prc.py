# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:54:09 2022

@author: hagem
"""

from Preprocessing_Functions import prc, prc_stretched, pv

fp = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'
fp_energy = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_1minute_power.csv'
S = "2022-10-15"
E = "2022-10-16"
t = prc(fp, S, E)
print(t)
#pv =  pv(fp_energy, S, E)
#print(pv.shape)
t_stretched = prc_stretched(t)
print(t_stretched, t_stretched.shape[0])