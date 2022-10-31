# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
"""
Bereite ein Skript vor, um die Daten nachher sinnvoll in die Optimierung aufzunehmen.
Die wichtigen Daten sind die Spotpreise am Markt, die als Referenz in der Optimierung genutzt werden.
Weiterhin sind durchschnittliche Verbrauchsdaten eines Haushalts hilfreich, und die Solardaten.

Arbeitsschritte:
    0. Finde vernünftige CSV-Dateien für alle Fragestellungen.
    1. Lese die csv-Dateien in Pandas ein (Möglicherweise auch in eine SQL-Datenbank?)
    2. Strukturiere die/das Panda-Dataframe
    3. 
    4. Speichere Tages-/Wochenprofile als np-Array oder Panda-Dataframe ab (Ersteres vlt. sinnvoller)
    4.1. -> Möglicherweise Skript schreiben, um Datei auszulesen, und Lastprofil(e) eines bestimmten Tages zu erhalten.
"""
"Zunächst: Spot-Markt Preise 2022"
spot_preise_2022 = pd.read_csv("C:/Users/hagem/Optimierung_Elektromanagement/CSV-Dateien/Spot-Markt Preise 2022/2022.csv")
spot_preise_2022 = spot_preise_2022.rename(columns={"date" : "Datum", "start_hour" : "Start", "end_hour" : "Ende", "price_euros_mwh": "Preis Euro/mWh"})
spot_preise_2022 = spot_preise_2022.drop(['volume_mwh', 'Ende'], axis=1)

spot_preise_2022["Datum"] = pd.to_datetime(spot_preise_2022["Datum"])
spot_preise_2022 = spot_preise_2022.loc[spot_preise_2022['Preis Euro/mWh'] <1500]
price_hour = spot_preise_2022.groupby(['Start'])

stundenpreise=[spot_preise_2022[spot_preise_2022["Start"]==hour]["Preis Euro/mWh"].to_numpy() for hour in spot_preise_2022['Start'].unique()]
fig, axs = plt.subplots(figsize=(16,4))
axs.set_ylabel("Preis [Euro/mWh]", fontsize=12, fontweight='bold')
axs.set_xlabel("Uhrzeit", fontsize=12, fontweight='bold')
axs.violinplot(stundenpreise)

"""
Verbrauchsdaten von Haushalten (z.B. Deutschland, Europa, Südafrika)
Ziel: Finde Daten, bestmöglich als csv, mit Tagesdurchschnittswerten der Haushaltsverbrauche
Ergebnis: Messdaten eines Studentenwohnheims: https://data.mendeley.com/v1/datasets/hwy83hpc6f/draft
Vergleichbarkeit dieser Daten sei einmal dahingestellt.
Idee: Um Szenarien für Verbrauch zu erstellen: Gruppiere nach Jahreszeit und sample Szenarien, alternativ
Verteilung approximieren und selber mögliche Verbrauchsszenarien erstellen, nichtparametrische Statistik.
"""

consmpt = pd.read_excel('C:/Users/hagem/Optimierung_Elektromanagement/CSV-Dateien//Verbrauchdaten Südafrika/all_hour.xlsx')
consmpt = consmpt.dropna()
consmpt['hour'] = consmpt['Time'].dt.hour
stundenverbrauch = [consmpt[consmpt['hour']==hour]['kWh'].to_numpy() for hour in consmpt['hour'].unique()]
#fig, axs = plt.subplots(figsize=(16,4))
#axs.set_ylabel("Verbrauch [kWh]", fontsize=12, fontweight='bold')
#axs.set_xlabel("Uhrzeit", fontsize=12, fontweight='bold')
#axs.violinplot(stundenverbrauch)


"""
Erzeugungsdaten von Solarkraft
Ziel: Finde Wetterdaten, bestmöglich als csv, mit täglichen Wetterdaten, primär Informationen
über tägliche Sonnenstrahlung
Ergebnis: Dateien von PVGIS, zuverlässige europäische Daten für beliebige Standorte in Europa & Afrika

"""

sd = pd.read_csv("C:/Users/hagem/Optimierung_Elektromanagement/CSV-Dateien/Solardaten/Timeseries_Globalstrahlung_Südafrika-28.817_24.992_SA2_1kWp_crystSi_14_0deg_0deg_2005_2020.csv", 
                 skiprows=11,
                 skipfooter=10,
                 usecols=[0,1,2,3],
                 header=0,
                 names=['Zeitpunkt', 'PV Leistung (W)', 'Globalstrahlung (W/m^2)', 'Sonnenhöhe (Grad)'],
                 dtype = {'PV Leistung (W)': np.float64, 'Globalstrahlung (W/m^2)': np.float64, 'Sonnenhöhe (Grad)': np.float64})
sd['Zeitpunkt'] = pd.to_datetime(sd['Zeitpunkt'], format='%Y%m%d:%H%M').dt.round('H')
print(sd.head())
sd_2020 = sd[sd['Zeitpunkt'].dt.year == 2020]
#sd_2020.where(sd['Zeitpunkt'] <= '2020-12-31').plot(x='Zeitpunkt')
