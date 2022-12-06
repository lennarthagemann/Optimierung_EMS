

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import load_df
from Analysis_Functions import charging_session_data, empirical_distr_total_energy, prob_daily_event, empirical_quantile, Remove_Outlier_Indices, classify_session, rayleigh_fit, rayleigh, pickle_probs
import pandas as pd
from collections import Counter
from scipy import stats

flpth = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_15minutes_power.csv'
flpth_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'

cols = ['Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
        'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)']

df = load_df(flpth)
df = df.drop(index=0, axis=0)
df = df.drop(columns='Zeit', axis=1)
df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix') +dt.timedelta(hours=2)
df['Uhrzeit'] = df['Zeitstempel'].dt.time
for col in ['Hausverbrauch (W)', 'Wärmepumpeverbrauch (W)','Ladepunktverbrauch (W)']:
	df[col] = df[col].astype(float)
	df[col] = df[col][df[col] >= 0]
df = df.round()



first_day = '2019-04-18'
last_day = '2022-10-18'
total_daily_energy_car = empirical_distr_total_energy(df, "Ladepunktverbrauch (W)", first_day, last_day, sort=True)
# total_daily_energy_car.hist(bins=3)
# total_daily_energy_car.plot()
# plt.show()

prob_charging_session = prob_daily_event(total_daily_energy_car)
print(prob_charging_session) # -> 75% aller Tage findet keine charging session statt.
print(empirical_quantile(0.95, total_daily_energy_car))
sp_index, sp_time, ep_index, ep_time, avg_load, max_load, total_energy = charging_session_data(df[["Zeitstempel", "Ladepunktverbrauch (W)"]])

charging_session_analysis = pd.DataFrame({"Startzeitpunkt" : pd.Series(sp_time, dtype='datetime64[s]'),
                                        "Endzeitpunkt" : pd.Series(ep_time, dtype='datetime64[s]'),
                                        "Durchschnittsleistung (W)" : pd.Series(avg_load, dtype='float32'),
                                        "Maximalleistung (W)" : pd.Series(max_load, dtype='float32'),
                                        "Gesamtleistung (kWh)" : pd.Series(total_energy, dtype='float32'),
                                        })
charging_session_analysis["Dauer"] = (charging_session_analysis["Endzeitpunkt"] - charging_session_analysis["Startzeitpunkt"]).dt.total_seconds()/60
print(charging_session_analysis[["Gesamtleistung (kWh)", "Maximalleistung (W)", "Durchschnittsleistung (W)", "Dauer"]].describe())
counts,bins,_ = plt.hist(charging_session_analysis["Gesamtleistung (kWh)"])
bins = bins[:-1] + np.diff(bins)/2
print(counts, '\n', bins)

clusters, probs_charging_speed = classify_session(charging_session_analysis)
print(f'Die Wahrscheinlichkeit für eine approximative Ladegeschwindigkeit von {probs_charging_speed[0][0]} W beträgt: {probs_charging_speed[0][1]}')
print(f'Die Wahrscheinlichkeit für eine approximative Ladegeschwindigkeit von {probs_charging_speed[1][0]} W beträgt: {probs_charging_speed[1][1]}')
print(f'Die Wahrscheinlichkeit für eine approximative Ladegeschwindigkeit von {probs_charging_speed[2][0]} W beträgt: {probs_charging_speed[2][1]}')
print(f'Die Wahrscheinlichkeit für eine approximative Ladegeschwindigkeit von {probs_charging_speed[3][0]} W beträgt: {probs_charging_speed[3][1]}')
pars, pcov  = rayleigh_fit(np.array(bins), np.array(counts))
print(f'Die optimalen Werte lauten für die Amplitude: {pars[0]}; Parameter der Rayleigh-Verteilung: {pars[1]}')
# fig, axs = plt.subplots(figsize=(12,12))
# axs.plot(np.linspace(bins[0], bins[-1], 10000), rayleigh(np.linspace(bins[0], bins[-1], 10000), *pars))
# axs.hist(charging_session_analysis["Gesamtleistung (kWh)"])
# plt.show()

print(charging_session_analysis["Dauer"])
# charging_session_analysis.hist(column=["Maximalleistung (W)", "Durchschnittsleistung (W)"], layout=(1,3), figsize=(16,4))									
# plt.hist(charging_session_analysis["Dauer"], bins=[15*i for i in range(50)], color="grey", edgecolor='yellow')
# plt.show()

# plt.scatter(charging_session_analysis['Dauer'].dt.total_seconds(), charging_session_analysis["Maximalleistung (W)"])
# plt.show()
# Gruppiere Werte nach Tradingfenster

charging_session_analysis["Startuhrzeit"] = (charging_session_analysis["Startzeitpunkt"].dt.hour*60) + (charging_session_analysis["Startzeitpunkt"].dt.minute)
print(charging_session_analysis["Startuhrzeit"])
start_count, start_bins, _ = plt.hist(charging_session_analysis["Startuhrzeit"], bins=[60*i for i in range(25)], color='yellow', edgecolor='black')
print(start_bins, '\n', start_count)
plt.show()

start_probs = start_count/(sum(start_count))
hourly_start_prob = {f"0{i}:00" if i < 10 else f"{i}:00" : el for i, el in enumerate(start_probs)}
for key in hourly_start_prob.keys():
    print(f'Wahrscheinlichkeit einer Ladesession zum Zeitpunkt {key} beträgt {hourly_start_prob[key]}')


"""
-------------------------
Speichere die Werte ab
-------------------------
"""

pickle_probs("C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Auto",
                data= [hourly_start_prob, prob_charging_session, probs_charging_speed, pars],
                names=["Startwahrscheinlichkeit", "Tägliche_Wahrscheinlichkeit ", "Wahrscheinlichkeit_Ladeleistung", "Parameter_Pareto_Gesamtenergie"])


# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Ladepunktverbrauch (W)'].mean(),  label='Ladepunkt')
# plt.show()

# # Stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]

# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.boxplot(car_quarter_hour)
# plt.show()