# -*- coding: utf-8 -*-

"""
-----------------------------------------
In dieser Datei stehen die nötigen Funktionen zur Datenanalyse. Folgende Fragestellungen sollen damit anschließend gelöst werden:
- Wie sieht die Verteilung von Hausverbrauch, Auto und Wärmepumpe aus? (stündlich, täglich, Wochentag/Wochenende)
- Mit welcher Wahrscheinlichkeit liegt zu einem bestimmtem Zeitpunkt
- An wie vielen Tagen wurde überhaupt geladen?


-> Schreibe eine Funktion um eine annähernde Wahrscheinlichkeitsverteilung mittels empirischer Verteilungsfunktion zu finden.
-----------------------------------------
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, pv, car, hp, load_df

def Remove_Outlier_Indices(df, min, max):
    Q1 = df.quantile(min)
    Q3 = df.quantile(max)
    IQR = Q3 - Q1
    trueList = ~((df < (Q1 - 1.5 * IQR)) |(df > (Q3 + 1.5 * IQR)))
    return trueList

def charging_session_start():
    """
	Finde den Startpunkt einer charging session. Erledige dies indem  wir die Zeitpunkte auswählen,
	in denen die letzte Zeit nich mehr geladen wurde (z.B. 15 Minuten) und dann für eine Mindestschwellenzeit wieder geladen wird,
	z.B. 5 Minuten.
	-----------
	Ausgabe: Ein Dataframe mit den Startzeitpunkten
    """
    return

def charging_session_length(Startpunkte):
	"""
	
	-----------
	Ausgabe: Neue Spalte mit Länge für die Startzeitpunkte
	"""
	return 

def charging_session_probability_daily():
	return

def charging_session_probability_hourly():
	return

def charging_session_probability_quarter_hourly():
	return

flpth = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_15minutes_power.csv'
flpth_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'

cols = ['Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
        'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)']

df = load_df(flpth)
df = df.drop(index=0, axis=0)
df = df.drop(columns='Zeit', axis=1)
df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
df['Uhrzeit'] = df['Zeitstempel'].dt.time
for col in ['Hausverbrauch (W)', 'Wärmepumpeverbrauch (W)','Ladepunktverbrauch (W)']:
        df[col] = df[col].astype(float)
df = df.round()

dmd = df['Hausverbrauch (W)'][df['Hausverbrauch (W)'] > 0]
hp = df['Wärmepumpeverbrauch (W)'][df['Wärmepumpeverbrauch (W)'] > 0]
car = df['Ladepunktverbrauch (W)'][df['Ladepunktverbrauch (W)'] > 0]

# Gruppiere Werte nach Tradingfenster

dmd_quarter_hour = [df[df['Uhrzeit']==zp]['Hausverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Hausverbrauch (W)'],0.25,0.75)] for zp in df['Uhrzeit'].unique()]
hp_quarter_hour = [df[df['Uhrzeit']==zp]['Wärmepumpeverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Wärmepumpeverbrauch (W)'],0.25,0.75)] for zp in df['Uhrzeit'].unique()]
car_quarter_hour = [df[df['Uhrzeit']==zp]['Ladepunktverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Ladepunktverbrauch (W)'],0.1,0.9)] for zp in df['Uhrzeit'].unique()]
print(car_quarter_hour)
# fig,axs = plt.subplots(1,3, figsize=(12,4))
# axs[0].bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Hausverbrauch (W)'].mean(), label='Haus')
# axs[1].bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Wärmepumpeverbrauch (W)'].mean(),  label='Wärmepumpe')
# axs[2].bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Ladepunktverbrauch (W)'].mean(),  label='Ladepunkt')
# plt.show()

#Stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]

fig,axs = plt.subplots(3,1, figsize=(12,4))
axs[0].boxplot(dmd_quarter_hour)
axs[1].boxplot(hp_quarter_hour)
axs[2].boxplot(car_quarter_hour)
plt.show()