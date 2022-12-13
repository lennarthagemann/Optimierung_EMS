from Analysis_Functions import home_consumption_quarterhourly_division, Remove_Outlier_Indices, empirical_distr_total_energy, classify_sessions, daily_load_group, pickle_probs
import sys
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import datetime as dt
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import load_df

flpth = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_15minutes_power.csv'

cols = ['Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
        'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)']

df = load_df(flpth)
df = df.drop(index=0, axis=0)
df = df.drop(columns='Zeit', axis=1)
seasons = ['Winter', 'Frühling', 'Sommer', 'Herbst']
df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix') + dt.timedelta(hours=2)
df['Uhrzeit'] = df['Zeitstempel'].dt.time
# Berechne die Jahreszeit für eine saisonale Analyse:
# 21.12 - 19.3 (Winter); 20.3 - 20.06 (Frühling); 21.06 - 22.09 (Sommer); 23.09-20.12 (Herbst)
df['Datum_Abstand'] = (df['Zeitstempel'].dt.month*100 + df['Zeitstempel'].dt.day + 10)%1231
df['Jahreszeit'] = pd.cut(df['Datum_Abstand'], [0,309,611,913,1211], labels=seasons)
print((pd.DataFrame({'Zeitwert': (df['Zeitstempel'].dt.month*100 + df['Zeitstempel'].dt.day + 10)%1231,'Zeitstempel' :  df['Zeitstempel'], 'Jahreszeit' : df['Jahreszeit']})))

for col in ['Hausverbrauch (W)', 'Wärmepumpeverbrauch (W)','Ladepunktverbrauch (W)']:
	df[col] = df[col].astype(float)
	df[col] = df[col][df[col] >= 0]
df = df.round()

first_day = '2019-04-18'
last_day = '2022-10-18'
total_daily_energy_pvs = pd.DataFrame({"total_energy" : [], "day" : [], "season" : []})
low_pvs, medium_pvs, high_pvs = pd.DataFrame({"total_energy" : [], "day" : []}), pd.DataFrame({"total_energy" : [], "day" : []}), pd.DataFrame({"total_energy" : [], "day" : []})
for label in seasons:    
    total_daily_energy_pv = empirical_distr_total_energy(df[df['Jahreszeit'] == label], "PV Leistung (W)", first_day, last_day)
    total_daily_energy_pv = total_daily_energy_pv[total_daily_energy_pv['total_energy'] > 0]
    ind = total_daily_energy_pv.index
    ind.name = label
    total_daily_energy_pvs.append(total_daily_energy_pv)
    low_pv, medium_pv, high_pv = classify_sessions(total_daily_energy_pv, quants=[0.33,0.66,1])
    low_pv['season'], medium_pv['season'], high_pv['season'] = label, label, label
    low_pvs = pd.concat([low_pvs, low_pv])
    medium_pvs = pd.concat([medium_pvs, medium_pv])
    high_pvs = pd.concat([high_pvs, high_pv])
print(low_pvs, medium_pvs, high_pvs)

low_pv_days, medium_pv_days, high_pv_days = [], [], []

low_pv_days = {label : daily_load_group(df, low_pvs[low_pvs['season'] == label], col_pow="PV Leistung (W)") for label in seasons}
medium_pv_days = {label : daily_load_group(df, medium_pvs[medium_pvs['season'] == label], col_pow="PV Leistung (W)") for label in seasons}
high_pv_days = {label : daily_load_group(df, high_pvs[high_pvs['season'] == label], col_pow="PV Leistung (W)") for label in seasons}
print(low_pv_days, medium_pv_days, high_pv_days)

plt.show()

pickle_probs("C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/PV",
                data= [low_pv_days, medium_pv_days, high_pv_days],
                names=["PV_niedrige_Erzeugung", "PV_mittlere_Erzeugung", "PV_hohe_Erzeugung"])

# Stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]

# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.boxplot(dmd_quarter_hour)
# plt.show()
