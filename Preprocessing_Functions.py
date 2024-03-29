# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 10:41:01 2022

@author: hagem
"""
import pandas as pd
import numpy as np
import datetime as dt

def load_df(filepath):
    df= pd.read_csv(filepath,
                sep=';',
                na_values='',
                false_values=[''],
                low_memory=False,
                header=1,
                names=['Zeit', 'Zeitstempel', 'Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
                        'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)'],
                )
    df = df.fillna(0)
    return df

def demand(date, demand, zeitpunkt, df, round=True):
    assert isinstance(date, str)
    """
    Parameter:
        date - Datum für das zu bestimmende Erzeugungsprofil, Format 'YYYY-MM-DD'
        demand - Name der Spalte des Dataframe, das Verbrauchsdaten des Haushalts enthält
        zeitpunkt - Name der Spalte die Zeitstempel enthält: Danach werden die Werte für das Tagesprofil
                    ausgewählt, Format in dieser Spalte muss mit 'date' Parameter übereinstimmen
        df - Dataframe 
    
    Ausgabe:
        np-Array mit float-Werten der PV-Erzeugung aus dem Dataframe. Länge des Arrays wird durch Anzahl der 
        Einträge zu dem jeweiligen Tag definiert, also implizit durch die Länge der Zeitschritte,
    gebe für ein gegebenes Dataframe und einen Tag im Format "YYYY-MM-DD" eine PV-ERzeugungskurve aus
    """
    assert isinstance(date, str)
    assert isinstance(demand, str)
    assert isinstance(zeitpunkt, str)
    df = df.set_index(zeitpunkt)
    demand_date = df.filter(like=date, axis=0)[demand].to_numpy()
    if round:
        demand_date = np.round(demand_date, decimals=0).astype(int)
    return demand_date

def dmd(df, Startdatum, Enddatum, round=True, smooth=True):
    """
    Lese den Verbrauch in einem bestimmten Zeitraum ein und speiche ihn als float64-numpy array.
    Interpretiere negative Werte als Messfehler und setze diese auf Null.
    Runde die Werte auf drei Nachkommastellen um die Maschinengenauigkeit nicht auszureizen
    """
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
    df['Hausverbrauch (W)'] = df['Hausverbrauch (W)'].astype(float)
    df['Hausverbrauch (W)'][df['Hausverbrauch (W)'] < 0] = 0
    df = df.query('@Startdatum <= Zeitstempel and @Enddatum > Zeitstempel' )
    dmd_date = df['Hausverbrauch (W)'].to_numpy()
    if smooth:
        dmd_date = moving_average(dmd_date)
    if round:
        dmd_date = np.round(dmd_date, decimals=0).astype(int)
    return dmd_date

def car(df, Startdatum, Enddatum, round=True, smooth=True):
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    
    df = df.drop(index=0, axis=0)
    df = df.drop(columns='Zeit', axis=1)
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
    df['Ladepunktverbrauch (W)'] = df['Ladepunktverbrauch (W)'].astype(float)
    df = df.query('@Startdatum <= Zeitstempel and @Enddatum > Zeitstempel' )
    car_date = df['Ladepunktverbrauch (W)'].to_numpy()
    if smooth:
        car_date = moving_average(car_date)
    if round:
        car_date = np.round(car_date, decimals=0).astype(int)

    return car_date

def price(Startdatum, Enddatum, preis, zeitpunkt, zeitschritt, df):
    assert isinstance(preis, str)
    assert isinstance(zeitpunkt, str)
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    assert isinstance(zeitschritt, int)
    assert 1 <= zeitschritt <= 60
    assert dt.datetime.strptime(Startdatum, "%Y-%m-$d") <= dt.datetime.strptime(Enddatum, "%Y-%m-$d")
    """
    Parameter:
        date - Datum für das zu bestimmende Preisprofil, Format 'YYYY-MM-DD'
        preis- Name der Spalte des Dataframe, das zeitvariable Preisdaten enthält
        zeitpunkt - Name der Spalte die Zeitstempel enthält: Danach werden die Werte für das Tagesprofil
                    ausgewählt, Format in dieser Spalte muss mit 'date' Parameter übereinstimmen
        df - Dataframe 
    
    Ausgabe:
        np-Array mit float-Werten der PV-Erzeugung aus dem Dataframe. Länge des Arrays wird durch Anzahl der 
        Einträge zu dem jeweiligen Tag definiert, also implizit durch die Länge der Zeitschritte,
    gebe für ein gegebenes Dataframe und einen Tag im Format "YYYY-MM-DD" eine PV-ERzeugungskurve aus
    """
    df = df.query('@Startdatum <= zeitpunkt and @Enddatum > zeitpunkt' )
    preis_date = np.round(df[preis].to_numpy(), decimals=3)
    return preis_date

def prc(filepath, Startdatum, Enddatum, round=True):
    assert isinstance(filepath, str)
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    #assert isinstance(Zeitschritt, int)
    spot = pd.read_csv(filepath,
                       skiprows=1, 
                       header=None,
                       sep=',"',
                       names=['Zeitraum', 'Day-ahead Preis (Eur/kWh)', 'Währung'])
    spot = spot.drop(labels='Währung', axis=1)
    spot['Zeitraum'] = spot['Zeitraum'].str.strip('"')
    spot['Zeitraum'] = pd.to_datetime(spot['Zeitraum'].str.slice(stop=16)) 
    spot['Zeitraum'] = spot['Zeitraum'].dt.strftime('%Y-%m-%d %H:%M:%S')
    spot['Day-ahead Preis (Eur/kWh)'] = (spot['Day-ahead Preis (Eur/kWh)'].str.strip('"'))
    spot = spot.drop_duplicates()
    spot = spot[spot['Day-ahead Preis (Eur/kWh)']!='-']
    spot['Day-ahead Preis (Eur/kWh)'] = spot['Day-ahead Preis (Eur/kWh)'].replace({'':'0'})
    spot['Day-ahead Preis (Eur/kWh)'] = spot['Day-ahead Preis (Eur/kWh)'].astype(float)/1000
    spot = spot.query('@Startdatum <= Zeitraum and @Enddatum > Zeitraum' )
    prc_date = spot['Day-ahead Preis (Eur/kWh)'].to_numpy()
    if round:
        prc_date =np.round(prc_date, decimals=2)
    return prc_date
    
def prc_stretched(prc):
    """
    Wenn wir das Problem in minütlichen Schritten lösen wollen, müssen wir die Preiskurce strecken,
    da die Spot-Preise sich nur jede Stunde ändern.
    Dafür müssen wir für den Gesamtzeitraum die 15 Minutenpreise für jede Minute im Zeitraum klonen.
    """
    mult = 15
    prc_stretched = np.array(np.zeros(prc.shape[0]*mult), dtype=float)
    for i in range(prc.shape[0]):
        prc_stretched[mult*i:mult*(i+1)] = prc[i] 
    return prc_stretched

def pv_generation(date, pv_generation, zeitpunkt, df):
    """
    Parameter:
        date - Datum für das zu bestimmende Erzeugungsprofil, Format 'YYYY-MM-DD'
        pv-generation - Name der Spalte des Dataframe, das PV-Erzeugundsaten enthält
        zeitpunkt - Name der Spalte die Zeitstempel enthält: Danach werden die Werte für das Tagesprofil
                    ausgewählt, Format in dieser Spalte muss mit 'date' Parameter übereinstimmen
        df - Dataframe 
    
    Ausgabe:
        np-Array mit float-Werten der PV-Erzeugung aus dem Dataframe. Länge des Arrays wird durch Anzahl der 
        Einträge zu dem jeweiligen Tag definiert, also implizit durch die Länge der Zeitschritte,
    gebe für ein gegebenes Dataframe und einen Tag im Format "YYYY-MM-DD" eine PV-ERzeugungskurve aus
    """
    assert isinstance(date, str)
    assert isinstance(pv_generation, str)
    assert isinstance(zeitpunkt, str)
    df = df.set_index(zeitpunkt)
    pv_date = df.filter(like=date, axis=0)[pv_generation].to_numpy();
    return pv_date

def pv(df, Startdatum, Enddatum, round=True, smooth=True):
    """
    Speichere die PV-Daten der Anlagen in einem bestimmtem Zeitraum  als numpy-Array mit float64 Werten.
    Runde die Werte auf drei Stellen um die Maschinengenauigkeit nicht ausreizen zu müssen.
    """

    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    df = df.drop(index=0, axis=0)
    df = df.drop(columns='Zeit', axis=1)
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
    df['PV Leistung (W)'] = df['PV Leistung (W)'].astype(float)
    df = df.query('@Startdatum <= Zeitstempel and @Enddatum > Zeitstempel' )
    df = df.set_index('Zeitstempel')
    pv = df['PV Leistung (W)'].to_numpy()
    if smooth:
        pv = moving_average(pv)
    if round:
        pv = np.round(pv, decimals=0).astype(int)

    return pv

def hp(df, Startdatum, Enddatum, round=True, smooth=True):
    """
    Verbrauch der Wärmepumpe in einem bestimmten Zeitrahmen als numpy-Array gerundet darstellen.
    """
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    df = df.drop(index=0, axis=0)
    df = df.drop(columns='Zeit', axis=1)
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
    df['Wärmepumpeverbrauch (W)'] = df['Wärmepumpeverbrauch (W)'].astype(float)
    df = df.query('@Startdatum <= Zeitstempel and @Enddatum > Zeitstempel' )
    df = df.set_index('Zeitstempel')
    hp = df['Wärmepumpeverbrauch (W)'].to_numpy()
    if smooth:
        hp = moving_average(hp)
    if round:
        hp = np.round(hp, decimals=0).astype(int)

    return hp


def moving_average(a, n=10):
    """
    Schreibe eine moving_average Funktion für PV, um die Kurve zu glätten.
    Wichtig: Diese soll die gleiche Dimension haben wie der Input!
    1. Berechne zur Zeit j die Summe der letzten min(j,n) Datenpunkten
    2. Teile diese jeweils durch min(j,n)
    """
    b = np.empty(np.shape(a)[0])
    for i in range(np.shape(a)[0]):
        if i < 10:
            b[i] = a[i]
        else:
            b[i]=sum(a[i-n+1:i+1])/n
    return b