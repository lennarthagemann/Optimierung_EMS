# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 10:41:01 2022

@author: hagem
"""
import pandas as pd
import numpy as np
import datetime as dt
def demand(date, demand, zeitpunkt, df):
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
    demand_date = df.filter(like=date, axis=0)[demand].to_numpy();
    return demand_date

def dmd(filepath, Startdatum, Enddatum):
    assert isinstance(filepath, str)
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    
    df= pd.read_csv(filepath,
                     sep=';',
                     na_filter=False,
                     low_memory=False,
                     names=['Zeit', 'Zeitstempel', 'Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
                            'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)'],
                    )
    df = df.drop(index=0, axis=0)
    df = df.drop(columns='Zeit', axis=1)
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
    df['Hausverbrauch (W)'] = df['Hausverbrauch (W)'].astype(float)
    df = df.query('@Startdatum <= Zeitstempel and @Enddatum > Zeitstempel' )
    dmd_date = df['Hausverbrauch (W)'].to_numpy();
    return dmd_date

def car(filepath, Startdatum, Enddatum):
    assert isinstance(filepath, str)
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    
    df= pd.read_csv(filepath,
                     sep=';',
                     na_filter=False,
                     low_memory=False,
                     names=['Zeit', 'Zeitstempel', 'Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
                            'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)'],
                    )
    df = df.drop(index=0, axis=0)
    df = df.drop(columns='Zeit', axis=1)
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
    df['Ladepunktverbrauch (W)'] = df['Ladepunktverbrauch (W)'].astype(float)
    df = df.query('@Startdatum <= Zeitstempel and @Enddatum > Zeitstempel' )
    car_date = df['Ladepunktverbrauch (W)'].to_numpy();
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
    print(df)
    preis_date = df[preis].to_numpy();
    return preis_date

def prc(filepath, Startdatum, Enddatum):
    assert isinstance(filepath, str)
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    #assert isinstance(Zeitschritt, int)
    spot = pd.read_csv(filepath,
                       skiprows=1,
                       engine='python',
                       header=None,
                       sep=',"',
                       names=['Zeitraum', 'Day-ahead Preis (Eur/kWh)', 'Währung'])
    spot = spot.drop(labels='Währung', axis=1)
    spot['Zeitraum'] = spot['Zeitraum'].str.strip('"')
    spot['Zeitraum'] = pd.to_datetime(spot['Zeitraum'].str.slice(stop=16)) 
    spot['Zeitraum'] = spot['Zeitraum'].dt.strftime('%Y-%m-%d %H:%M:%S')
    print(spot)
    spot['Day-ahead Preis (Eur/kWh)'] = (spot['Day-ahead Preis (Eur/kWh)'].str.strip('"'))
    spot = spot.drop_duplicates()
    spot = spot[spot['Day-ahead Preis (Eur/kWh)']!='-']
    spot['Day-ahead Preis (Eur/kWh)'] = spot['Day-ahead Preis (Eur/kWh)'].replace({'':'0'})
    spot['Day-ahead Preis (Eur/kWh)'] = spot['Day-ahead Preis (Eur/kWh)'].astype(float)/1000
    spot = spot.query('@Startdatum <= Zeitraum and @Enddatum > Zeitraum' )
    print(spot)
    prc_date = np.round(spot['Day-ahead Preis (Eur/kWh)'].to_numpy(), 4)
    return prc_date
    
def prc_stretched(prc, days):
    """
    Wenn wir das Problem in minütlichen Schritten lösen wollen, müssen wir die Preiskurce strecken,
    da die Spot-Preise sich nur jede Stunde ändern.
    Dafür müssen wir für den Gesamtzeitraum die 15 Minutenpreise für jede Minute im Zeitraum klonen.
    """
    prc_stretched = np.array(np.zeros(1440 * days), dtype=float)
    assert int((1440 * days)/prc.shape[0]) == 15
    mult = 15
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

def pv(filepath, Startdatum, Enddatum):
    assert isinstance(filepath, str)
    assert isinstance(Startdatum, str)
    assert isinstance(Enddatum, str)
    df= pd.read_csv(filepath,
                     sep=';',
                     na_filter=False,
                     low_memory=False,
                     names=['Zeit', 'Zeitstempel', 'Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
                            'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)'],
                    )
    df = df.drop(index=0, axis=0)
    df = df.drop(columns='Zeit', axis=1)
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], unit='s', origin='unix')
    df['PV Leistung (W)'] = df['PV Leistung (W)'].astype(float)
    df = df.query('@Startdatum <= Zeitstempel and @Enddatum > Zeitstempel' )
    df = df.set_index('Zeitstempel')
    pv = df['PV Leistung (W)'].to_numpy();
    return pv

def moving_average_full_dim(a, n=4) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n