import pickle
from Analysis_Functions import *
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import bernoulli, rv_discrete, rayleigh
import numpy as np
"""
---------------------
Erstelle eine Wahrscheinlichkeitsverteilung für die Ladesessions eines Autos.

1.Wahrscheinlichkeit ob Ladesession passiert
2.Wahrscheinlichkeiten für einen bestimmten Startzeitpunkt je nach Tag, z.B. früh morgens oder am Feierabend wahrscheinlicher
3.Wahrscheinlichkeit für die zu ladende Energiemenge
4.Wahrscheinlichkeit für die genutzte Ladeleistung
--> Damit lässt sich 
---------------------
"""

car_path = 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Auto'

with open(car_path + "/Startwahrscheinlichkeit.pkl", 'rb') as f:
    car_start_prob = pickle.load(f)

with open(car_path + "/Tägliche_Wahrscheinlichkeit .pkl", 'rb') as f:
    car_daily_prob = pickle.load(f)

with open(car_path + "/Wahrscheinlichkeit_Ladeleistung.pkl", 'rb') as f:
    car_power_prob = pickle.load(f)

with open(car_path + "/Parameter_pareto_Gesamtenergie.pkl", 'rb') as f:
    car_energy_prob = pickle.load(f)

car_daily_sample = bernoulli.rvs(car_daily_prob, size=1)
car_start_distr = rv_discrete(name='Daytime Start Distribution', values=([int(el[:2]) for el in car_start_prob.keys()], list(car_start_prob.values())))
car_power_distr = rv_discrete(name="Charging Power Distribution", values=([a[0] for a in car_power_prob], [a[1] for a in car_power_prob]))
car_power_sample = car_power_distr.rvs(size=1)
car_energy_distr = rayleigh(scale=abs(car_energy_prob[1]))
total_energy = car_energy_prob[0]*np.array(car_energy_distr.rvs(size=1))
car_start_sample = car_start_distr.rvs(size=1)
print(car_daily_sample)
print(car_start_sample)
print(car_power_sample)
print(total_energy)
print(f"Die notwendige Ladezeit beträgt: {total_energy/car_power_sample}")
_,_,remaining_minutes = loading_session_division((total_energy/car_power_sample)[0])
rem_avg_pwr = float_to_minute(remaining_minutes, car_power_sample[0])
print(remaining_minutes, rem_avg_pwr)