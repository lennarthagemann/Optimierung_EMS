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
    plt.show()

def multiscale_load_curve_plot(split, dates1, prc1, pv1, dmd1, car1, hp1, buy1, bat_use1, bat_charge1, dates2, prc2, pv2, dmd2, car2, hp2, buy2, bat_use2, bat_charge2):
    
    """
    Lastprofil innerhalb eines bestimmten Zeitraums, chronologischer Verlauf.
    Problem hier: wir müssen auf verschiedene Zeitskalen achten, jeweils für die beiden Schritte.
    Diese sollen in einem Bild nacheinander geplottet werden.
    Idee: Konkateniere die Arrays, sorge dafür das in der zweiten Zeitstufe der Abstand der xticks größer ist.
    """

    dates = dates1 + dates2
    prc = prc1 + prc2
    pv = pv1 + pv2
    dmd = dmd1 + dmd2
    car = car1 + car2
    hp = hp1 + hp2
    buy = buy1 + buy2
    bat_use = bat_use1 + bat_use2
    bat_charge = bat_charge1 + bat_charge2
    steps1 = [int(el.split('t')[1]) for el in dates1]
    steps2 = [split*(int(el.split('t')[1])+1) for el in dates2]
    steps = steps1 + steps2
    print(f'battery use : {bat_use}')
    print(f'battery charging : {bat_charge}')
    fig, axs = plt.subplots(constrained_layout=True)
    axs.step(steps, prc, label='price', alpha=0.3)
    axs.step(steps, pv, label='pv')
    axs.step(steps, [i+j+k for i,j,k in zip(dmd, car, hp)], label='demand')
    axs.step(steps, buy, label='Energy_Bought')
    axs.step(steps, bat_use, label='Bat-Use')
    axs.step(steps, bat_charge, label='Bat-Charge')
    axs.legend(loc='upper left', fontsize='x-small')
    #axs.set_xlim(lims)
    for label in axs.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('right')
    plt.show()

def all_scenarios_load_curve_plot(scenarios_x, scenarios_y, dates, prc, pv, dmd, car, hp, buy, bat_use, bat_charge):
    """
    Lastprofile für alle Szenarien. In einem Gitter (mit scenarios_x * scenarios_y = Anzahl Szenarien) wird für
    jedes Szenario das Ergebnis der Optimierung visualisiert.
    Die Daten werden hier listenweise gegeben und durch Iteration über die zweidimensionalen Indize aufgerufen.
    """
    fig, axs = plt.subplots(scenarios_x, scenarios_y, constrained_layout=True)
    for i, ax in enumerate(fig.axes):
        ax.step(dates[i], 5000*prc, label='price', alpha=0.3)
        ax.step(dates[i], pv[i], label='pv')
        ax.step(dates[i], [j+k+l for j,k,l in zip(dmd[i], car[i], hp[i])], label='demand')
        ax.step(dates[i], buy[i], label='Energy_Bought')
        ax.step(dates[i], bat_use[i], label='Bat-Use')
        ax.step(dates[i], bat_charge[i], label='Bat-Charge')
    axs[0][0].legend(loc='upper left', fontsize='small')
    plt.show()