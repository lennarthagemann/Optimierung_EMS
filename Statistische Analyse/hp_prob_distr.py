import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import load_df
from Analysis_Functions import  hp_session_data, Remove_Outlier_Indices, empirical_distr_total_energy

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
print(df.describe())

first_day = '2019-04-18'
last_day = '2022-10-18'
total_daily_energy_hp= empirical_distr_total_energy(df, "Wärmepumpeverbrauch (W)", first_day, last_day, sort=True)
total_daily_energy_hp.hist()
total_daily_energy_hp.plot()
plt.show()

hp_quarter_hour = [df[df['Uhrzeit']==zp]['Wärmepumpeverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Wärmepumpeverbrauch (W)'],0.25,0.75)] for zp in df['Uhrzeit'].unique()]

day = df[("2020-03-08 00:00" <= df["Zeitstempel"]) & ("2020-03-09 00:00" > df["Zeitstempel"])]
print(day)
plt.step(day["Zeitstempel"], day["Wärmepumpeverbrauch (W)"])
plt.show()

hps_index, hps_time, hpe_index, hpe_time, hp_avg_load, hp_max_load = hp_session_data(df[["Zeitstempel", "Wärmepumpeverbrauch (W)"]])
hp_analysis = pd.DataFrame({"Startzeitpunkt" : hps_time,
							"Endzeitpunkt" : hpe_time,
							"Durchschnittsleistunng (W)" : hp_avg_load,
							"Maximalleistung (W)" : hp_max_load})
print(hp_analysis)

# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Wärmepumpeverbrauch (W)'].mean(),  label='Wärmepumpe')
# plt.show()

# Stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]

# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.boxplot(hp_quarter_hour)
# plt.show()