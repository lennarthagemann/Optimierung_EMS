import sys
import os
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, pv, car, hp, load_df
import datetime as dt
import numpy as np
import pickle 
from Analysis_Functions import *
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import bernoulli, rv_discrete, rayleigh

"""
----------------------------------------------------------------------
In diesem Skript sollen die Szenariodaten und Szenariostruktur implementiert werden,
auf Basis der ermittelten statistischen Daten. Dabei ist die schwierigste
Frage die Gewichtung der Szenarien.
----------------------------------------------------------------------
"""

filepath_15min = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_15minutes_power.csv'
filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'

car_path = 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Auto'
hp_path = 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Wärmepumpe'
dmd_path = 'C:/Users/hagem/Optimierung_EMS/Statistische Analyse/Ergebnisse/Biblis/Hausverbrauch'

def create_scenario_structure():
    return

def create_scenarios(sampling_sun=True):
    """
    Konstruiere die Szenariodaten und speichere diese ab.

    -sampling_sun=True => Wähle einen gesampeltenn Tag für den Ertrag der PV-Anlage. Falls explizit False gesetzt wird, wird je ein 
    Tag
    """
    return