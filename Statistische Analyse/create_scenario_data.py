import pickle
import os
import sys
import shutil
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, car, hp, load_df
from Analysis_Functions import *
sys.path.append('C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/scenario_generation')
# from scenario_generation import scenario_data_generator
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import bernoulli, rv_discrete, rayleigh
import numpy as np


np.random.seed(seed=23342327)

"""
-------------------------------------------------------------------------
-                                  PV                                   -
-------------------------------------------------------------------------

"""
scenario_count = 6 #Anzahl der Szenarien, also verschiedener Lastprofile die generiert und erstellt werden sollen.
energy_factor = 4 # =60/15, dient zur Berechnung der Energie, hängt stets von der Zeitskala ab (hier 15-minütige Schritte).
x_timeframe = np.arange(start=0,stop=1440,step=15) #Beobachtungszeitraum ist ein 24-Stunden Fenster mit 15-minütigen Zeitschritten
pv_path = 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/PV'

with open(pv_path + "/PV_niedrige_Erzeugung.pkl", 'rb') as f:
    pv_low_sessions = pickle.load(f)

with open(pv_path + "/PV_mittlere_Erzeugung.pkl", 'rb') as f:
    pv_medium_sessions = pickle.load(f)

with open(pv_path + "/PV_hohe_Erzeugung.pkl", 'rb') as f:
    pv_high_sessions = pickle.load(f)

season = 'Herbst'
if season:
    pv_low_sessions = pv_low_sessions[season]
    pv_medium_sessions = pv_medium_sessions[season]
    pv_high_sessions = pv_high_sessions[season]

pv_load_distr = rv_discrete(name="Distribution power class heat pump", values=([0, 1, 2], [1/3 for i in range(3)]))
pv_index_low_distr = rv_discrete(name="Distribution low heat pump", values=([i for i in range(len(pv_low_sessions))], [1/len(pv_low_sessions) for i in range(len(pv_low_sessions))]))
pv_index_medium_distr = rv_discrete(name="Distribution low heat pump", values=([i for i in range(len(pv_medium_sessions))], [1/len(pv_medium_sessions) for i in range(len(pv_medium_sessions))]))
pv_index_high_distr = rv_discrete(name="Distribution low heat pump", values=([i for i in range(len(pv_high_sessions))], [1/len(pv_high_sessions) for i in range(len(pv_high_sessions))]))
pv_load_sample = pv_load_distr.rvs(size=scenario_count)

pv = np.empty(scenario_count, dtype=object)
for i, pv_gen_index in enumerate(pv_load_sample):
    if pv_gen_index == 0:
        print("Niedrige Erzeugung von PV-Strom.")
        pv[i] = np.array(pv_low_sessions[pv_index_low_distr.rvs(size=scenario_count)][0])
    if pv_gen_index == 1:
        print("Mittlere Erzeugung von PV-Strom.")
        pv[i] = np.array(pv_medium_sessions[pv_index_medium_distr.rvs(size=scenario_count)][0])
    if pv_gen_index == 2:
        print("Hohe Erzeugung von PV-Strom.")
        pv[i] = np.array(pv_high_sessions[pv_index_high_distr.rvs(size=scenario_count)][0])

"""
-------------------------------------------------------------------------
-                                  Auto                                 -
-------------------------------------------------------------------------

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


car_daily_sample = bernoulli.rvs(car_daily_prob, size=scenario_count) #Ladet das Auto heute oder nicht?
car_start_distr = rv_discrete(name='Daytime Start Distribution', values=([int(el[:2]) for el in car_start_prob.keys()], list(car_start_prob.values()))) #Wann startet die Ladesession?
car_power_distr = rv_discrete(name="Charging Power Distribution", values=([a[0] for a in car_power_prob], [a[1] for a in car_power_prob]))# Welche Ladeleistung wird genutzt (approximativ)
quarter_hour_distr = rv_discrete(name="Quarter Hour Distribution", values=([0, 15, 30, 45], [0.25 for i in range(4)])) #Zu welcher Viertelstunde soll gestartet werden? (gleichverteilt) 
car_power_sample = np.array(car_power_distr.rvs(size=scenario_count))  # Array der zufällig bestimmten durchschnittlichen Ladeleistungen
car_energy_distr = rayleigh(scale=abs(car_pareto_sigma[car_power_sample[0]]))
total_energy = car_pareto_amp[car_power_sample[0]]*np.array(car_energy_distr.rvs(size=scenario_count)) #Array der zu ladenden Gesamtenergie (abhängig von Durchschnittsladeleistung)
car_start_sample = np.array(car_start_distr.rvs(size=scenario_count))*60 #Array der zufällig bestimmten Startzeiten
quarter_hour_sample = np.array(quarter_hour_distr.rvs(size=scenario_count)) #Array der zufällig bestimmten Viertelstunden der jeweiligen Startstunde
full_hours ,full_minutes, remaining_minutes = loading_session_division((total_energy/car_power_sample)) #Berechnet die vollen Stunden, vollen 15 Minuten und Restminuten für die Ladesession

total_start = car_start_sample + quarter_hour_sample
full_step_stop = total_start + full_minutes 
total_stop = full_step_stop + remaining_minutes
rem_avg_pwr = float_to_minute(remaining_minutes, car_power_sample[0])

for i, sample in enumerate(car_daily_sample):
    if sample == 1:
        print(f"Die Ladegeschwindigkeit in W: {car_power_sample[i]}, die zu ladende Energie: {total_energy[i]}")
        print(f"Die notwendige Ladezeit beträgt: {total_energy[i]/car_power_sample[i]}")
        print(f"Die Startzeit lautet: {total_start[i]}")
        print(f"Die (in Abhängigkeit der gesampelten Gesamtmenge {total_energy[i]}) bestehende Stopzeit lautet: {total_stop[i]}")
        print(f"Dabei wird von {total_start[i]} bis {full_step_stop[i]} mit {car_power_sample[i]} geladen, \n"
        f"bis {total_stop[i]} mit {rem_avg_pwr[i]} (auf die Viertelstunde gesehen)")
    else:
        print("Heute keine Ladesession!")
y_car = np.empty(scenario_count, dtype=object)
for j in range(scenario_count):
    y_car[j] = np.array([car_daily_sample[j]*car_power_sample[j] if((i * 15 >= total_start[j]) & (i*15 <= total_stop[j])) else 0 for i  in range(len(x_timeframe))])
    y_car[j][np.argmin([i if (i*15 > full_step_stop[j]) else len(x_timeframe) for i in range(len(x_timeframe))])] += car_daily_sample[j]*rem_avg_pwr[j]

"""
-------------------------------------------------------------------------
-                               Wärmepumpe                              -
-------------------------------------------------------------------------
"""

hp_path = 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Wärmepumpe'

with open(hp_path + "/Wärmesessions_niedrige_Last.pkl", 'rb') as f:
    hp_low_sessions= pickle.load(f)

with open(hp_path + "/Wärmesessions_mittlere_Last.pkl", 'rb') as f:
    hp_medium_sessions = pickle.load(f)

with open(hp_path + "/Wärmesessions_hohe_Last.pkl", 'rb') as f:
    hp_high_sessions = pickle.load(f)

hp_load_distr = rv_discrete(name="Distribution power class heat pump", values=([0, 1, 2], [1/3 for i in range(3)]))
hp_index_low_distr = rv_discrete(name="Distribution low heat pump", values=([i for i in range(len(hp_low_sessions))], [1/len(hp_low_sessions) for i in range(len(hp_low_sessions))]))
hp_index_medium_distr = rv_discrete(name="Distribution low heat pump", values=([i for i in range(len(hp_medium_sessions))], [1/len(hp_medium_sessions) for i in range(len(hp_medium_sessions))]))
hp_index_high_distr = rv_discrete(name="Distribution low heat pump", values=([i for i in range(len(hp_high_sessions))], [1/len(hp_high_sessions) for i in range(len(hp_high_sessions))]))
hp_load_sample = hp_load_distr.rvs(size=scenario_count)

y_hp = np.empty(scenario_count, dtype=object)
for i,hp_load_index in enumerate(hp_load_sample):
    if hp_load_index == 0:
        print("Niedrige Auslastung der Wärmepumpe.")
        y_hp[i] = np.array(hp_low_sessions[hp_index_low_distr.rvs(size=scenario_count)][0])
    if hp_load_index == 1:
        print("Mittlere Auslastung der Wärmepumpe.")
        y_hp[i] = np.array(hp_medium_sessions[hp_index_medium_distr.rvs(size=scenario_count)][0])
    if hp_load_index == 2:
        print("Hohe Auslastung der Wärmepumpe.")
        y_hp[i] = np.array(hp_high_sessions[hp_index_high_distr.rvs(size=scenario_count)][0])

"""
-------------------------------------------------------------------------
-                             Hausverbrauch                             -
-------------------------------------------------------------------------

"""
dmd_path = 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Hausverbrauch'

with open(dmd_path + "/Hausverbrauch_niedrige_Last.pkl", 'rb') as f:
    dmd_low_sessions= pickle.load(f)

with open(dmd_path + "/Hausverbrauch_mittlere_Last.pkl", 'rb') as f:
    dmd_medium_sessions = pickle.load(f)

with open(dmd_path + "/Hausverbrauch_hohe_Last.pkl", 'rb') as f:
    dmd_high_sessions = pickle.load(f)

dmd_load_distr = rv_discrete(name="Distribution power class demand", values=([0, 1, 2], [1/3 for i in range(3)]))
dmd_index_low_distr = rv_discrete(name="Distribution low demand", values=([i for i in range(len(dmd_low_sessions))], [1/len(dmd_low_sessions) for i in range(len(dmd_low_sessions))]))
dmd_index_medium_distr = rv_discrete(name="Distribution medium demand", values=([i for i in range(len(dmd_medium_sessions))], [1/len(dmd_medium_sessions) for i in range(len(dmd_medium_sessions))]))
dmd_index_high_distr = rv_discrete(name="Distribution high demand", values=([i for i in range(len(dmd_high_sessions))], [1/len(dmd_high_sessions) for i in range(len(dmd_high_sessions))]))
dmd_load_sample = dmd_load_distr.rvs(size=scenario_count)

y_dmd = np.empty(scenario_count, dtype=object)
for i, sample in enumerate(dmd_load_sample):
    if sample == 0:
        print("Niedrige Auslastung im Haus.")
        y_dmd[i] = np.array(dmd_low_sessions[dmd_index_low_distr.rvs(size=scenario_count)][0])
    if sample == 1:
        print("Mittlere Auslastung im Haus.")
        y_dmd[i] = np.array(dmd_medium_sessions[dmd_index_medium_distr.rvs(size=scenario_count)][0])
    if sample == 2:
        print("Hohe Auslastung im Haus.")
        y_dmd[i] = np.array(dmd_high_sessions[dmd_index_high_distr.rvs(size=scenario_count)][0])


"""
-------------------------------------------------------------------------
-     Speichere die gesampelten Daten zur späteren Visualisierung       -
-------------------------------------------------------------------------
"""

filepath_sampled_data = 'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/Samples'

filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'
Startdatum = '2022-07-21 00:00'
Enddatum = '2022-07-22 00:00'
prc_biblis = prc(filepath_spot, Startdatum, Enddatum)
categories = ['hp', 'dmd', 'pv', 'car', 'prc']
if os.path.exists(filepath_sampled_data):
    shutil.rmtree(filepath_sampled_data)
    os.makedirs(filepath_sampled_data)
else:
    os.makedirs(filepath_sampled_data)

for cat in categories:
    if os.path.exists(filepath_sampled_data + f'/{cat}'):
        shutil.rmtree(filepath_sampled_data + f'/{cat}')
        os.makedirs(filepath_sampled_data + f'/{cat}')
    else:
        os.makedirs(filepath_sampled_data + f'/{cat}')    

for i in range(scenario_count):
    with open(filepath_sampled_data + f'/hp/hp_{i}', 'wb') as f:
        pickle.dump(y_hp[i], f)
    with open(filepath_sampled_data + f'/dmd/dmd_{i}', 'wb') as f:
       pickle.dump(y_dmd[i], f)
    with open(filepath_sampled_data + f'/pv/pv_{i}', 'wb') as f:
        pickle.dump(pv[i], f)
    with open(filepath_sampled_data + f'/car/car_{i}', 'wb') as f:
        pickle.dump(y_car[i], f)
with open(filepath_sampled_data + f'/prc/prc', 'wb') as f:
    pickle.dump(prc_biblis, f)

"""
-------------------------------------------------------------------------
-           Generation der Szenariodaten und -struktur                  -
-------------------------------------------------------------------------

"""

scenario_filepath = 'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/scenarios/'
steps = [f't{i}' for i in range(len(x_timeframe))]


print(y_car[0], y_dmd[0], y_hp[0], prc_biblis)

if os.path.exists(scenario_filepath):
    shutil.rmtree(scenario_filepath)
    os.makedirs(scenario_filepath)
else:
    os.makedirs(scenario_filepath)

#Generiere die Szenariodaten (so viele wie durch scenario_count gewünscht sind)

for i in range(scenario_count):
    with open(scenario_filepath + f'scenario{i}.dat','w') as f:
        # Schreibe die generierten Lastprofile 
        f.write('set steps := ')
        for t in steps:
            f.write(t + " ")
        f.write('; \n')
        f.write('param pv := ')
        for t, value in zip(steps, pv[i]):
            f.write(f'{t} {value} ')
        f.write('; \n')
        f.write('param d := ')
        for t, value in zip(steps, y_dmd[i]):
            f.write(f'{t} {value} ')
        f.write('; \n')
        f.write('param dcar := ')
        for t, value in zip(steps, y_car[i]):
            f.write(f'{t} {value} ')
        f.write('; \n')
        f.write('param price := ')
        for t, value in zip(steps, prc_biblis):
            f.write(f'{t} {value} ')
        f.write('; \n')
        f.write('param hp := ')
        for t, value in zip(steps, y_hp[i]):
            f.write(f'{t} {value} ')
        f.write('; \n')
        f.write(f'param M := {10**7}; \n')
        f.write(f'param C_max := {200000}; \n')
        f.write(f'param C_Start := {0}; \n')
        f.write(f'param energy_factor := {energy_factor}; \n')
        

# Erzeuge die Szenariostruktur 

probs = [1/scenario_count for _ in range(scenario_count)]
scenarionames = [str(i) for i in range(scenario_count)]
if len(probs) > 1:
    probs[1] += (1 - sum(probs)) 
print(probs)
assert sum(probs) == 1
with open('C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/scenarios/ScenarioStructure.dat', 'w') as f:
    f.write('set Stages := FirstStage SecondStage ; \n')
    f.write('set Nodes := RootNode \n')
    for name in scenarionames:
        f.write(f'Node{name} \n')
    f.write('; \n')
    f.write('param NodeStage := RootNode FirstStage \n')
    for name in scenarionames:
        f.write(f"Node{name} SecondStage \n")
    f.write("; \n")
    f.write('set Children[RootNode] := ')
    for name in scenarionames:
        f.write(f'Node{name} \n')
    f.write('; \n')
    f.write("param ConditionalProbability := RootNode 1.0 \n")
    for name, prob in zip(scenarionames, probs):
        f.write(f"Node{name} {prob} \n")
    f.write("; \n")
    f.write("set Scenarios := ")
    for name in scenarionames:
        f.write(f"Scenario{name} \n")
    f.write('; \n')
    f.write("param ScenarioLeafNode := " )
    for name in scenarionames:
        f.write(f"Scenario{name}  Node{name} \n")
    f.write('; \n')
    f.write("set StageVariables[FirstStage] := z1[*]; \n")
    f.write("set StageVariables[SecondStage] := p_kauf[*] \n p_bat_Nutz[*] \n p_bat_Lade[*] \n p_einsp[*] \n bat[*] \n p_Nutz[*]; \n")
    f.write('param StageCost := FirstStage FirstStageCost \n SecondStage SecondStageCost;')