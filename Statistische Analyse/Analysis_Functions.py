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
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import scipy as scp
import pickle
import os
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
	Ausgabe: Ein Dataframe mit den Startzeitpunkten, Endzeitpunkten, Ladezeit, durchschnittliche Ladeleistung und der Gesamtenergie.
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

def classify_sessions(df_energy, col_en='total_energy', col_day='day', quants=[0.3,0.6,0.9]):
	"""
	Input: Dataframe mit den täglichen Energiewerten
	Output: 3 Dataframes mit dem jeweiligen Tag für niedrigen, mittleren oder hohen Verbrauch, ermittelt über die Quantile
	"""
	low = df_energy[[col_en, col_day]][df_energy[col_en] <= df_energy.quantile(quants[0])[0]]
	medium = df_energy[[col_en, col_day]][(df_energy[col_en] >= df_energy.quantile(quants[0])[0]) & (df_energy[col_en] <= df_energy.quantile(quants[1])[0])]
	high = df_energy[[col_en, col_day]][(df_energy[col_en] >= df_energy.quantile(quants[1])[0]) & (df_energy[col_en] <= df_energy.quantile(quants[2])[0])]
	return low, medium, high

def daily_load_group(df, df_group, col_pow, col_day='day', col_time='Zeitstempel'):
	"""
	Lese all die Tage ein aus 'df_group', speichere für jeden Tag die tägliche Kurve aus 'df' als Numpy-Array.
	Ausgabe: Mehrdimensinonales np-Array (Array von Arrays) mit allen aufgeschlüsselten Verbräuchen in praktischer Form.
 	"""
	group_load_curves = []
	for day in df_group[col_day].unique():
		group_load_curves.append(df[col_pow][(df[col_time] < dt.datetime.strptime(day,'%Y-%m-%d') + dt.timedelta(days=1) ) & (df[col_time] >= dt.datetime.strptime(day, '%Y-%m-%d'))])
	return np.array(group_load_curves)

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
			"total_energy" : [df[col][df["Zeitstempel"] < tup[1]][df["Zeitstempel"] >= tup[0]].sum()*energy_factor*0.001 for tup in day_range]
			}
		).sort_values(by=["total_energy"])
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

def classify_session(df, col="Durchschnittsleistung (W)", bins=[3300, 6600, 11000, 22000]):
	"""
	Ordne die Ladesessions einem ungefähren Ladeniveau zu, welches zu einem bestimmmten Typ passt.
	Nutze dazu cdist von scipy (benötigt min. 2-dim Input), um das näheste Cluster zu finden.
	Output: -Zuordnung der maximalen Ladeleistungen zu den Clustern
	-Anteile/Wahrscheinlichkeit für eine bestimmte Ladeleistung
	"""
	cluster_2d = [[e,0] for e in bins]
	powers = [[el, 0] for el in df[col].to_numpy()]
	distances = scp.spatial.distance.cdist(powers, cluster_2d, 'minkowski', p=1)
	print(distances)
	closest_powers = [cluster_2d[el][0] for el in distances.argmin(axis=1)]
	session_dict = {powers[i][0] : closest_powers[i] for i in range(len(closest_powers))}
	probs = list(zip(bins,[val/len(session_dict.values()) for val in Counter(session_dict.values()).values()]))
	return probs, [closest_powers[i] for i in range(len(df[col].to_numpy()))]

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

def rayleigh(x, amplitude, sigma):
	"""
	x muss np-Array sein! Berechnet die Wahrscheinlichkeitsdichtefunktion der rayleigh-Funktion
	"""
	return amplitude *(x / (sigma)**2 * np.exp(-x**2/(2*sigma**2)))

def rayleigh_scaled(x, sigma, height=1, scale=1):
	return height*(x*scale)/sigma**2 * np.exp(-(x*scale)**2/(2*sigma**2))

def rayleigh_fit(xdata, ydata, f=rayleigh, normalized=False):
	"""
	Passe die Rayleigh-Verteilung (oder eine andere Funktion) an die Daten an,
	z.B. Rayleigh an die Gesamtverbräche der Ladesessions. 
	"""
	if not normalized:
		y = ydata/float(sum(ydata))
	x = np.arange(1,len(xdata)+1)
	popt, pcov = scp.optimize.curve_fit(f,xdata, ydata, p0=(100,10))
	return popt, pcov

def pickle_probs(dest, data, names):
	"""
	Speichere die Werte aus der Analyse so ab, dass sie seperat wieder geladen werden können um damit Lastsprofile zu erstellen
		-dest : Genereller Speicherort, wird mit Aufruf der Funktion erstellt
		-data : Liste mit Daten die gespeichert werden sollen
		-names : Liste mit Namen der zugehörigen Variablen 
	"""
	assert 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse' in dest
	assert type(data) == list
	assert type(names) == list
	assert len(data) == len(names)
	if not os.path.exists(dest):
		os.makedirs(dest)
	for el,name in zip(data, names):
		with open(dest +"/"+ name + ".pkl", 'wb') as f:
			pickle.dump(el, f)

def loading_session_division(time):
	"""
	Teile die Ladesessions so auf, das wir wissen wie viele 15 Minuten Schritte gemacht wurden,
	und wie groß der letzte Zeitbruchteil ist der kürzer als 15 Minuten ist
	Input: Float mit Minuten hintern Komma (aber in Dezimaldarstallung)
	"""
	hours = int(time)
	remaining_minutes = int(round((time - int(time))*(60/100),2)*100) % 15
	minutes = int(round((time - int(time))*(60/100),2)*100) - remaining_minutes
	return hours, minutes, remaining_minutes

def float_to_minute(remaining_minutes, power):
	"""
	Berechne die verbleibende Anzahl in Minuten und die durchschnittliche Leistung
	im letzten Schritt (Abbrechender 15 Minuten Teil) 
	"""
	assert remaining_minutes <= 15
	remaining_avg_power = power * (remaining_minutes/15)
	return remaining_avg_power

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