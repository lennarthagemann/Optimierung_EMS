import pyomo.environ as pe
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, pv, car, hp
import pandas as pd
import numpy as np
import datetime as dt

timeformat = '%Y-%m-%d %H:%M'
timestep = 1
energy_factor = timestep/60

filepath = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_1minute_power.csv'
filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'
Startdatum = '2022-05-08 00:00'
Enddatum = '2022-05-08 01:00'
delta = int((dt.datetime.strptime(Enddatum, timeformat) - dt.datetime.strptime(Startdatum, timeformat)).total_seconds()/60)

steps = [f"t{i}" for i in range(delta)]
dmd_biblis = dmd(filepath, Startdatum, Enddatum) 
prc_biblis = prc(filepath_spot, Startdatum, Enddatum)
if timestep == 1:
    prc_biblis = prc_stretched(prc_biblis)
pv_biblis = pv(filepath, Startdatum, Enddatum)
car_biblis = car(filepath, Startdatum, Enddatum)
hp_biblis = hp(filepath, Startdatum, Enddatum)

with open('C:/Users/hagem/Optimierung_EMS/Optimierung_Wohnhaus/AbstractModel/scenarios/scenario.dat', 'w') as f:
    f.write('set steps := ')
    for t in steps:
        f.write(t + " ")
    f.write('; \n')
    f.write('param pv := ')
    for t, pv in zip(steps, pv_biblis):
        f.write(f'{t} {pv} ')
    f.write('; \n')
    f.write('param d := ')
    for t, value in zip(steps, dmd_biblis):
        f.write(f'{t} {value} ')
    f.write('; \n')
    f.write('param dcar := ')
    for t, value in zip(steps, car_biblis):
        f.write(f'{t} {value} ')
    f.write('; \n')
    f.write('param price := ')
    for t, value in zip(steps, prc_biblis):
        f.write(f'{t} {value} ')
    f.write('; \n')
    f.write('param hp := ')
    for t, value in zip(steps, hp_biblis):
        f.write(f'{t} {value} ')
    f.write('; \n')
    f.write(f'param M := {10**5}; \n')
    f.write(f'param C_max := {20000}; \n')