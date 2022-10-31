# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Preprocessing_Functions import pv_generation, price, moving_average_full_dim, demand

filepath = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/BIblis_15minutes_power.csv'
start = '2022-10-03'
ende = '2022-10-10'
biblis = pd.read_csv(filepath,
                     sep=';',
                     na_filter=False,
                     low_memory=False,
                     names=['Zeit', 'Zeitstempel', 'Netzeinspeisung (W)', 'Netzbezug (W)', 'Batterienutzung (W)', 'Batterieeinspeisung (W)',
                            'PV Leistung (W)', 'Hausverbrauch (W)', 'Ladepunktverbrauch (W)', 'Wärmepumpeverbrauch (W)'],
                    )
biblis = biblis.drop(index=0, axis=0)
biblis = biblis.drop(columns='Zeit', axis=1)
biblis['Zeitstempel'] = pd.to_datetime(biblis['Zeitstempel'], unit='s', origin='unix')
biblis['PV Leistung (W)'] = biblis['PV Leistung (W)'].astype(float)

day_pv_gen = pv_generation(start, 'PV Leistung (W)', 'Zeitstempel', biblis)
x = np.arange(np.shape(day_pv_gen)[0])
#plt.step(x, day_pv_gen, color = 'grey', where='mid')
#plt.grid(axis='x', color='0.95')
#plt.title('PV-Erzeugungskurve ' + '2022-10-03')
start = '2022-10-03'
biblis['Hausverbrauch (W)'] = biblis['Hausverbrauch (W)'].astype(float)
day_demand =  demand(start, 'Hausverbrauch (W)', 'Zeitstempel', biblis)
x_1 = np.arange(np.shape(day_demand)[0])
#plt.step(x_1, day_demand, color = 'grey', where='mid')
filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'

spot = pd.read_csv(filepath_spot,
                   skiprows=1,
                   engine='python',
                   header=None,
                   sep=',"',
                   names=['Zeitraum', 'Day-ahead Preis (Eur/MWh)', 'Währung'])
spot = spot.drop(labels='Währung', axis=1)
spot['Zeitraum'] = spot['Zeitraum'].str.strip('"')
spot['Zeitraum'] = pd.to_datetime(spot['Zeitraum'].str.slice(stop=16)) 
spot['Zeitraum'] = spot['Zeitraum'].dt.strftime('%Y-%m-%d %H:%M:%S')
spot['Day-ahead Preis (Eur/MWh)'] = (spot['Day-ahead Preis (Eur/MWh)'].str.strip('"'))
spot = spot.drop_duplicates()
spot = spot[spot['Day-ahead Preis (Eur/MWh)']!='-']
spot['Day-ahead Preis (Eur/MWh)'] = spot['Day-ahead Preis (Eur/MWh)'].replace({'':'0'})
spot['Day-ahead Preis (Eur/MWh)'] = spot['Day-ahead Preis (Eur/MWh)'].astype(float)
day_spot = price('2022-03-01', 'Day-ahead Preis (Eur/MWh)', 'Zeitraum', spot)

#plt.step(np.arange(np.shape(day_spot)[0]), day_spot)
#plt.plot(np.arange(np.shape( moving_average(day_spot))[0]), moving_average(day_spot))
fig,axs = plt.subplots()
pv_plot = axs.plot(day_pv_gen, label='PV-Generation')
demand_plot = axs.plot(day_demand, label='Verbrauch')
spot_plot = axs.plot(day_spot, label='Preis auf dem Day-Ahead Markt')
axs.legend(fontsize='x-small', borderpad=0.2)