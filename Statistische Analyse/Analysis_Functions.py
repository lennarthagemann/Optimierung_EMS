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
import scipy as scp
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
	total_energy = []
	for s,e in timerange:
			loads = df["Ladepunktverbrauch (W)"][df["Zeitstempel"] >= s][df["Zeitstempel"] <= e]
			max_load = max(loads)
			avg_load = sum(loads)/len(loads)
			energy = avg_load * 0.001 * len(loads) * 0.25
			avg_loads.append(avg_load)
			max_loads.append(max_load)
			total_energy.append(energy)
	return startindex, starttimes, endindex, endtimes, avg_loads, max_loads, total_energy


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

def empirical_distr_total_energy(df, col, first_day, last_day, energy_factor=0.25, sort=False):
	"""
	Gibt die empirische Verteilung der Gesamtenergie eines Tages zurück.
	Dadurch lässt sich einordnen wie häufig hohe Verbrauchstage/niedrige Verbrauchstage vorkommen
	"""
	days = pd.date_range(start=first_day, end=last_day).strftime("%Y-%m-%d").to_numpy()
	day_range = [(days[i], days[i+1]) for i in range(len(days)-1)]
	if sort:
		total_daily_energy = pd.DataFrame({
			"day" : days[:-1],
			"total_energy" : sorted([df[col][df["Zeitstempel"] < tup[1]][df["Zeitstempel"] >= tup[0]].sum()*energy_factor*0.001 for tup in day_range])
			}
		)
	else:
				total_daily_energy = pd.DataFrame({
			"day" : days[:-1],
			"total_energy" : [df[col][df["Zeitstempel"] < tup[1]][df["Zeitstempel"] >= tup[0]].sum()*energy_factor*0.001 for tup in day_range]
			}
		)
	return total_daily_energy

def prob_daily_event(df, col='total_energy', threshold=0):
	"""
	Wahrscheinlichkeit das ein Event über den Betrachtungszeitraum eingetreten ist, z.B. Gesamthausverbrauch kleiner als
	Schwellenwert, oder Wahrscheinlichkeit für keine Ladesession (threshold=0) 
	"""
	p = df[col][df[col] <= threshold].count()/df[col].count()
	return p
def classify_session(df, col="Maximalleistung (W)"):
	cluster = [3300]
	session_dict = {}
	return session_dict
def empirical_quantile(prob,df_energy, col='total_energy',sorted=True):
	"""
	Finde anhand der empirischen Verteilung das Quantil zur Wahrscheinlichkeit 'prob',
	also den Wert so dass mit Wahrscheinlichkeit 'prob' die beobachteten Werte kleiner sind.
	Dieser ist ziemlich sicher nicht exakt gegeben
	"""
	n = df_energy[col].count()
	if sorted:
		quant = df_energy[col].iloc[int(prob*n)]
	return quant

# def curve_fitting_empirical_distr(df_energy, col='total_energy', gauss=True):
# 	"""
# 	Passe zu der empirischen Verteilung eine Kurve an, normalerweise eine Normalverteilung.
# 	Letztlich hilfreich um eventuell neue Lastprofile zu generieren.
# 	Hierzu muss die Kurve normiert werden, nachher kann dies wieder rückgängig gemacht werden.
# 	"""
# 	f = lambda x,mu,sigma: scp.stats.norm(mu,sigma).cdf(x) # Normalverteilung
# 	x = np.linspace(-1,1, df_energy[col].count())
# 	data = df_energy[col]
# 	mu, sigma = scp.optimize.curve_fit(f,x,data)[0]
# 	return curve