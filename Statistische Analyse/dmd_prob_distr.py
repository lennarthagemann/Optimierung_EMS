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
flpth_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'

cols = ['Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
        'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)']

df = load_df(flpth)
df = df.drop(index=0, axis=0)
df = df.drop(columns='Zeit', axis=1)
df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix') + dt.timedelta(hours=2)
df['Uhrzeit'] = df['Zeitstempel'].dt.time
for col in ['Hausverbrauch (W)', 'Wärmepumpeverbrauch (W)','Ladepunktverbrauch (W)']:
	df[col] = df[col].astype(float)
	df[col] = df[col][df[col] >= 0]
df = df.round()

first_day = '2019-06-30'
last_day = '2022-10-18'
total_daily_energy_dmd = empirical_distr_total_energy(df, "Hausverbrauch (W)", first_day, last_day, sort=False)
low_dmd, medium_dmd, high_dmd = classify_sessions(total_daily_energy_dmd)
total_daily_energy_dmd.hist()
total_daily_energy_dmd.plot()
print(total_daily_energy_dmd)

low_dmd_days = daily_load_group(df, low_dmd, col_pow="Hausverbrauch (W)")
medium_dmd_days = daily_load_group(df, medium_dmd, col_pow="Hausverbrauch (W)")
high_dmd_days = daily_load_group(df, high_dmd, col_pow="Hausverbrauch (W)")
print(low_dmd_days, medium_dmd_days, high_dmd_days)
days = [(f'2019-05-{i + 1}', f'2019-05-{i + 2}' )for i in range(1)]
print(days)

df['delta'] = df['Hausverbrauch (W)'].diff()
fig, axs = plt.subplots(figsize=(16,4))
for day in days:
        axs.plot(np.arange(96), df['delta'][(df['Zeitstempel'] < day[1])][df['Zeitstempel'] >= day[0]])
        axs.plot(np.arange(96), df['Hausverbrauch (W)'][(df['Zeitstempel'] < day[1])][df['Zeitstempel'] >= day[0]])
plt.show()
print(df)
dmd_quarter_hour = [df[df['Uhrzeit']==zp]['Hausverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Hausverbrauch (W)'],0.25,0.75)] for zp in df['Uhrzeit'].unique()]

fig,axs = plt.subplots(1,3, figsize=(12,4))
fig.suptitle("Mittelwert, Standardabweichung und Median des Hausverbrauchs")
width = 0.35
for ax in axs:
        ax.set_ylabel('Leistung (W)')
axs[0].bar(np.arange(0,24) - width/2, df.groupby(df['Zeitstempel'].dt.hour)['Hausverbrauch (W)'].mean(), width, label='Haus')
axs[0].bar(np.arange(0,24) + width/2, df.groupby(df['Zeitstempel'].dt.hour)['delta'].mean(), width, label='Haus')
axs[0].set_xlabel('Stunde')
axs[0].set_title('Mittelwert')
axs[1].bar(np.arange(0,24) - width/2, df.groupby(df['Zeitstempel'].dt.hour)['Hausverbrauch (W)'].std(), width, label='Haus')
axs[1].bar(np.arange(0,24) + width/2, df.groupby(df['Zeitstempel'].dt.hour)['delta'].std(), width, label='Haus')
axs[1].set_xlabel('Stunde')
axs[1].set_title('Standardabweichung')
axs[2].bar(np.arange(0,24) - width/2, df.groupby(df['Zeitstempel'].dt.hour)['Hausverbrauch (W)'].median(), width, label='Haus')
axs[2].bar(np.arange(0,24) + width/2, df.groupby(df['Zeitstempel'].dt.hour)['delta'].median(), width, label='Haus')
axs[2].set_xlabel('Stunde')
axs[2].set_title('Median')
plt.show()

pickle_probs("C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Hausverbrauch",
                data= [low_dmd_days, medium_dmd_days, high_dmd_days],
                names=["Hausverbrauch_niedrige_Last", "Hausverbrauch_mittlere_Last", "Hausverbrauch_hohe_Last"])

# Stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]

# fig,axs = plt.subplots(1,1, figsize=(12,4))
# axs.boxplot(dmd_quarter_hour)
# plt.show()
