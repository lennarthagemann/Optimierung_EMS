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
from Preprocessing_Functions import load_df

def Remove_Outlier_Indices(df, min, max):
    Q1 = df.quantile(min)
    Q3 = df.quantile(max)
    trueList = ~((df < Q1) |(df > Q3))
    return trueList

def charging_session_data(df):
	"""
	Finde den Startpunkt einer Lade-/Wärmepumpe session. Erledige dies indem  wir die Zeitpunkte auswählen,
	in denen die letzte Zeit nich mehr geladen wurde (z.B. 15 Minuten) und dann für eine Mindestschwellenzeit wieder geladen wird,
	z.B. 5 Minuten.
	=> Da wir hier alle 15 Minuten nur Datenpunkte erhalten ist dies nicht nötig, vergleiche mit dem vorigen/anschließendem Datenpunkt.
	
	-----------
	Eingabe: Dataframe mit der Zeit und den Leistungen 
	Ausgabe: Ein Dataframe mit den Startzeitpunkten, Endzeitpunkten, Ladezeit und durchschnittliche Ladeleistung.
	"""
	index  = df.index.values
	startindex = []
	starttimes = []
	for index in range(1,len(index)):
		if index >= 2:
			if df["Ladepunktverbrauch (W)"].iloc[index] > 0 and df["Ladepunktverbrauch (W)"].iloc[index - 1] == 0:
				startindex.append(index)
				starttimes.append(df["Zeitstempel"].iloc[index])
		else:
			continue
	endindex = []
	endtimes = []
	for i in range(starttimes.__len__()):
		# Indikator 'ind' dafür da das nur der tatsächliche (erste) Punkt zwischen zwei Lade sessions erkannt wird der Null ist.
		ind = 1
		if i < starttimes.__len__() -1 :
			for j in range(startindex[i], startindex[i+1]):
				if df["Ladepunktverbrauch (W)"].iloc[j] == 0 and ind:
					endindex.append(j)
					endtimes.append(df["Zeitstempel"].iloc[j])
					ind = 0
		else: 
			for j in range(startindex[i], df.index.values.max()):
				if df["Ladepunktverbrauch (W)"][j] == 0 and ind:
					endindex.append(j)
					endtimes.append(df["Zeitstempel"].iloc[j])
					ind = 0
	timerange = zip(starttimes,endtimes)
	avg_loads = []
	max_loads = []
	for s,e in timerange:
			loads = df["Ladepunktverbrauch (W)"][df["Zeitstempel"] >= s][df["Zeitstempel"] <= e]
			max_load = max(loads)
			avg_load = sum(loads)/len(loads)
			avg_loads.append(avg_load)
			max_loads.append(max_load)
	return startindex, starttimes, endindex, endtimes, avg_loads, max_loads


def hp_session_data(df):
	"""
	Finde den Startpunkt einer Lade-/Wärmepumpe session. Erledige dies indem  wir die Zeitpunkte auswählen,
	in denen die letzte Zeit nich mehr geladen wurde (z.B. 15 Minuten) und dann für eine Mindestschwellenzeit wieder geladen wird,
	z.B. 5 Minuten.
	=> Da wir hier alle 15 Minuten nur Datenpunkte erhalten ist dies nicht nötig, vergleiche mit dem vorigen/anschließendem Datenpunkt.
	
	-----------
	Eingabe: Dataframe mit der Zeit und den Leistungen 
	Ausgabe: Ein Dataframe mit den Startzeitpunkten, Endzeitpunkten, Ladezeit und durchschnittliche Ladeleistung.
	"""
	index  = df.index.values
	startindex = []
	starttimes = []
	for index in range(1,len(index)):
		if index >= 2:
			if df["Wärmepumpeverbrauch (W)"].iloc[index] >90 and df["Wärmepumpeverbrauch (W)"].iloc[index - 1] <= 85:
				startindex.append(index)
				starttimes.append(df["Zeitstempel"].iloc[index])
		else:
			continue
	endindex = []
	endtimes = []
	for i in range(starttimes.__len__()):
		# Indikator 'ind' dafür da das nur der tatsächliche (erste) Punkt zwischen zwei Lade sessions erkannt wird der Null ist.
		ind = 1
		if i < starttimes.__len__() -1 :
			for j in range(startindex[i], startindex[i+1]):
				if df["Wärmepumpeverbrauch (W)"].iloc[j] == 0 and ind:
					endindex.append(j)
					endtimes.append(df["Zeitstempel"].iloc[j])
					ind = 0
		else: 
			for j in range(startindex[i], df.index.values.max()):
				if df["Wärmepumpeverbrauch (W)"][j] == 0 and ind:
					endindex.append(j)
					endtimes.append(df["Zeitstempel"].iloc[j])
					ind = 0
	timerange = zip(starttimes,endtimes)
	avg_loads = []
	max_loads = []
	for s,e in timerange:
			loads = df["Wärmepumpeverbrauch (W)"][df["Zeitstempel"] >= s][df["Zeitstempel"] <= e]
			max_load = max(loads)
			avg_load = sum(loads)/len(loads)
			avg_loads.append(avg_load)
			max_loads.append(max_load)
	return startindex, starttimes, endindex, endtimes, avg_loads, max_loads

def home_consumption_quarterhourly_division(df):
	"""
	Analysiere den Hausverbrauch über den gesamten Zeitverlauf in 15 Minutenschritten.
	Relevant ist eine Wahhrscheinlichkeitsverteilung für alle Zeitpunkte.
	Dafür muss ein guter fit mit einer stetigen Wahrscheinlichkeitsverteilung gefunden werden.
	------------------
	Input: Dataframe mit Uhrzeiten (zur Gruppierung) und den Verbrauchsdaten
	Output: Eine List mit Dataframes für den 15-Minuten-Takt. Vorbereitend für eine weitere Analyse.
	"""
	quarter_hour_dfs = []
	for val in pd.unique(df["Uhrzeit"]):
		tempdf = df["Hausverbrauch (W)"][df["Uhrzeit"] == val]
		quarter_hour_dfs.append(tempdf)
	return quarter_hour_dfs

def home_consumption_deltas(df):
	"""
	Führe eine Analyse durch über die Abstände zwischen zwei Zeitpunkten jeweils in den Dataframes.
	Diese ist notwendig um eine sinnvolle Zeitreihe zu erstellen, einzelne Werte zwischen den Zeitintervallen zu 
	vergleichen/verbinden ist nicht hinreichend wegen der hohen Standardabweichung zwischen den Zeitpunkten.
	Dies ist nur beim Hausverbrauch sinnvoll da die anderen Verbraucher im System diskreteren Stufenverbrauch haben.
	------------------
	Input: Liste mit Dataframes der stündlichen Werte.
	Output: Statistische Werte zu den Übergängen zwischen zwei Zeitpunkten für alle Stunden/Zeitpunke.
	"""
	df["delta"] = df["Hausverbrauch (W)"].diff().shift(-1)

def time_between_charging_sessions(starttimes, length, df):
	"""
	Ermittle die Zeit zwischen zwei verschiedenen charging sessions. Danach kann man wie mittels einer gemischten Verteilung
	in einem Zeithorizont mit einer geometrischen Verteilung den Abstand (Zeit bis zum nächsten Beginn) simulieren.
	"""
	return 

def charging_session_probability_daily():
	"""
	Wie viele charging sessions kommen pro Tag vor? 
	Gebe eine Wahrscheinlichkeitsverteilung, indem je nach Anzahl von Startpunkten eines bestimmten Tages
	-----------
	Ausgabe:
	"""
	return

def charging_session_probability_hourly():
	"""

	-----------
	Ausgabe:
	"""
	return


def charging_session_probability_quarter_hourly():
	"""
	
	-----------
	Ausgabe:
	"""
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
print(df.describe())

cons_15min = home_consumption_quarterhourly_division(df)
for el in cons_15min:
	print(el[Remove_Outlier_Indices(el, 0.1, 0.9)].describe(), el.describe())

sp_index, sp_time, ep_index, ep_time, avg_load, max_load = charging_session_data(df[["Zeitstempel", "Ladepunktverbrauch (W)"]])


charging_session_analysis = pd.DataFrame({"Startzeitpunkt" : sp_time, 
											"Endzeitpunkt" : ep_time, 
											"Durchschnittsleistung (W)" : avg_load,
											"Maximalleistung (W)" : max_load
											})

# charging_session_analysis["Dauer"] = charging_session_analysis["Endzeitpunkt"].dt.hour*60 + charging_session_analysis["Endzeitpunkt"].dt.minute - (charging_session_analysis["Startzeitpunkt"].dt.hour*60 + charging_session_analysis["Startzeitpunkt"].dt.minute)
# print(charging_session_analysis["Dauer"], charging_session_analysis['Durchschnittsleistung (W)'] * charging_session_analysis['Dauer'])
#print(df[(df['Zeitstempel'] >= charging_session_analysis['Startzeitpunkt']) & (df['Zeitstempel'] <= charging_session_analysis['Endzeitpunkt'])])
#charging_session_analysis["Durchschnittliche Ladeleistung (W)"] = np.mean(df["Ladepunktverbrauch (W)"][(df['Zeitstempel'] >= charging_session_analysis['Startzeitpunkt']) & 
#(df['Zeitstempel'] <= charging_session_analysis['Endzeitpunkt'])])
# hist = charging_session_analysis.hist(column=["Maximalleistung (W)", "Durchschnittsleistung (W)", "Dauer"], layout=(1,3), figsize=(16,4))									
# plt.show()

# plt.scatter(charging_session_analysis['Dauer'], charging_session_analysis["Maximalleistung (W)"])
# plt.show()
# Gruppiere Werte nach Tradingfenster

# dmd_quarter_hour = [df[df['Uhrzeit']==zp]['Hausverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Hausverbrauch (W)'],0.25,0.75)] for zp in df['Uhrzeit'].unique()]
# hp_quarter_hour = [df[df['Uhrzeit']==zp]['Wärmepumpeverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Wärmepumpeverbrauch (W)'],0.25,0.75)] for zp in df['Uhrzeit'].unique()]
# car_quarter_hour = [df[df['Uhrzeit']==zp]['Ladepunktverbrauch (W)'][Remove_Outlier_Indices(df[df['Uhrzeit']==zp]['Ladepunktverbrauch (W)'],0.1,0.9)] for zp in df['Uhrzeit'].unique()]
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

# fig,axs = plt.subplots(1,3, figsize=(12,4))
# axs[0].bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Hausverbrauch (W)'].mean(), label='Haus')
# axs[1].bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Wärmepumpeverbrauch (W)'].mean(),  label='Wärmepumpe')
# axs[2].bar(np.arange(0,24), df.groupby(df['Zeitstempel'].dt.hour)['Ladepunktverbrauch (W)'].mean(),  label='Ladepunkt')
# plt.show()

#Stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]

# fig,axs = plt.subplots(3,1, figsize=(12,4))
# axs[0].boxplot(dmd_quarter_hour)
# axs[1].boxplot(hp_quarter_hour)
# axs[2].boxplot(car_quarter_hour)
# plt.show()