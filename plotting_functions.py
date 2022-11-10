"""
Plotting Funktionen für die Ergebnisse aus der Optimierung.

1.Plot der die Ergebnisse aus der Optimierung über das Zeitfenster darstellt.
"""

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator
import matplotlib.units as munits

def load_curve_plot(dates, prc, pv, dmd, car, hp, buy, bat_use, bat_charge):
    """
    Lastprofil innerhalb eines bestimmten Zeitraums, chronologischer Verlauf.
    Nimmt an das dates eine Liste von datetime Objekten ist, Im Format %Y-%m-%d %H:%M.
    """
    fig, axs = plt.subplots(constrained_layout=True)
    axs.step(dates, 5000*prc, label='price', alpha=0.3)
    axs.step(dates, pv, label='pv')
    axs.step(dates, dmd + car + hp, label='demand')
    axs.step(dates, buy, label='Energy_Bought')
    axs.step(dates, bat_use, label='Bat-Use')
    axs.step(dates, bat_charge, label='Bat-Charge')
    axs.legend(loc='upper left', fontsize='x-small')
    #axs.set_xlim(lims)
    for label in axs.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('right')
    axs.fmt_xdata = DateFormatter('%H:%M')
    fig.autofmt_xdate()
    plt.show()