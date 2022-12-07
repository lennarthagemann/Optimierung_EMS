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
3.Wahrscheinlichkeit für die genutze Ladeleistung
4.Wahrscheinlichkeit für die Gesamtenergie (bedingte Wahrscheinlichkeit je nach Ladeleistung mit Pareto)
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

with open(car_path + "/Parameter_Pareto_Amplitude.pkl", 'rb') as f:
    car_pareto_amp = pickle.load(f)

with open(car_path + "/Parameter_Pareto_Sigma.pkl", 'rb') as f:
    car_pareto_sigma = pickle.load(f)


car_daily_sample = bernoulli.rvs(car_daily_prob, size=1)
car_start_distr = rv_discrete(name='Daytime Start Distribution', values=([int(el[:2]) for el in car_start_prob.keys()], list(car_start_prob.values())))
car_power_distr = rv_discrete(name="Charging Power Distribution", values=([a[0] for a in car_power_prob], [a[1] for a in car_power_prob]))
quarter_hour_distr = rv_discrete(name="Quarter Hour Distribution", values=([0, 15, 30, 45], [0.25 for i in range(4)]))
car_power_sample = car_power_distr.rvs(size=1)
car_energy_distr = rayleigh(scale=abs(car_pareto_sigma[car_power_sample[0]]))
total_energy = car_pareto_amp[car_power_sample[0]]*np.array(car_energy_distr.rvs(size=1))
car_start_sample = np.array(car_start_distr.rvs(size=1))*60
quarter_hour_sample = quarter_hour_distr.rvs(size=1)

full_hours ,full_minutes, remaining_minutes = loading_session_division((total_energy/car_power_sample)[0]) 
full_time = full_hours*60 + full_minutes
total_start = car_start_sample + quarter_hour_sample
full_step_stop = total_start + full_time 
total_stop = full_step_stop+ remaining_minutes
rem_avg_pwr = float_to_minute(remaining_minutes, car_power_sample[0])

if car_daily_sample:
    print(f"Die Ladegeschwindigkeit in W: {car_power_sample}, die zu ladende Energie: {total_energy}")
    print(f"Die notwendige Ladezeit beträgt: {total_energy/car_power_sample}")
    print(f"Die Startzeit lautet: {total_start}")
    print(f"Die (in Abhängigkeit der gesampelten Gesamtmenge {total_energy}) bestehende Stopzeit lautet: {total_stop}")
    print(f"Dabei wird von {total_start} bis {total_start + full_time } mit {car_power_sample} geladen, \n"
     f"bis {total_stop} mit {rem_avg_pwr} (auf die Viertelstunde gesehen)")
else:
    print("Heute keine Ladesession!")

print(remaining_minutes, rem_avg_pwr)

"""
_____________________________
Plotte das Lastprofil
_____________________________

"""

x_timeframe = np.arange(start=0,stop=1440,step=15)
y = np.array([car_daily_sample[0]*car_power_sample[0] if((i * 15 >= total_start) & (i*15 <= total_stop)) else 0 for i  in range(len(x_timeframe))])
y[np.argmin([i if (i*15 >= full_step_stop) else len(x_timeframe) for i in range(len(x_timeframe))])] = car_daily_sample[0]*rem_avg_pwr
print(x_timeframe, y)

fig, axs = plt.subplots(figsize=(16,4))
axs.bar(x_timeframe, y, width=15)
plt.show()