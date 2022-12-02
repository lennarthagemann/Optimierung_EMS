"""
---------------------

Erstelle eine Wahrscheinlichkeitsverteilung für die Ladesessions eines Autos.

-Geometrische Verteilung für das Ankommen eines neuen E-Autos: Je länger die letzte Ladesession her ist,
desto wahrscheinlichlciher wird es, das wieder geladen wird (Aber die Person kann anderswo geladen haben,
weswegen dies keine echte Wahrscheinlichkeitsverteilung seien soll, aber mindestens monoton steigend.)
-Wahrscheinlichkeiten für einen bestimmten Startzeitpunkt je nach Tag, z.B. früh morgens oder am Feierabend wahrscheinlicher
-Wahrscheinlichkeit der Dauer je nach approximativer Ladegeschwindigkeit
-


---------------------
"""

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import load_df
from Analysis_Functions import charging_session_data, empirical_distr_total_energy, prob_daily_event, empirical_quantile, Remove_Outlier_Indices, classify_session
import pandas as pd
from collections import Counter
from scipy import stats

class car_distr(stats.rv_continuous):
    def _cdf(self, x):
        return
    def _stats(self):
        return

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
print(charging_session_analysis[["Gesamtleistung (kWh)", "Maximalleistung (W)", "Durchschnittsleistung (W)"]].describe())

clusters, probs = classify_session(charging_session_analysis)
print(clusters, '\n', probs)

plt.hist(clusters.values(), bins=[0, 3300, 6600, 11000, 22000])
plt.show()

charging_session_analysis["Dauer"] = charging_session_analysis["Endzeitpunkt"] - charging_session_analysis["Startzeitpunkt"]
print(charging_session_analysis["Dauer"], charging_session_analysis['Durchschnittsleistung (W)'] * charging_session_analysis['Dauer'].dt.total_seconds()/(60*60*1000))
# print(df[df['Zeitstempel'] >= charging_session_analysis['Startzeitpunkt']][df['Zeitstempel'] <= charging_session_analysis['Endzeitpunkt']])
# charging_session_analysis["Durchschnittliche Ladeleistung (W)"] = np.mean(df["Ladepunktverbrauch (W)"][(df['Zeitstempel'] >= charging_session_analysis['Startzeitpunkt']) & 
# (df['Zeitstempel'] <= charging_session_analysis['Endzeitpunkt'])])
# hist = charging_session_analysis.hist(column=["Maximalleistung (W)", "Durchschnittsleistung (W)", "Dauer"], layout=(1,3), figsize=(16,4))									
# plt.show()

# plt.scatter(charging_session_analysis['Dauer'].dt.total_seconds(), charging_session_analysis["Maximalleistung (W)"])
# plt.show()
# Gruppiere Werte nach Tradingfenster

# car_quarter_hour = [df[df['Uhrzeit']==zp]['Ladepunktverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Ladepunktverbrauch (W)'],0.1,0.9)] for zp in df['Uhrzeit'].unique()]

# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Ladepunktverbrauch (W)'].mean(),  label='Ladepunkt')
# plt.show()

# # Stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]

# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.boxplot(car_quarter_hour)
# plt.show()