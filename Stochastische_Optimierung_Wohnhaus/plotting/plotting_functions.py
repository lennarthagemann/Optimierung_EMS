"""
Plotting Funktionen für die Ergebnisse aus der Optimierung.

1.Plot der die Ergebnisse aus der Optimierung über das Zeitfenster darstellt.
"""

import matplotlib.pyplot as plt

def load_curve_plot(dates, prc, pv, dmd, car, hp, buy, bat_use, bat_charge):
    fig, axs = plt.subplots(constrained_layout=True)
    axs.step(dates, 5000*prc, label='price', alpha=0.3)
    axs.step(dates, pv, label='pv')
    axs.step(dates, dmd + car + hp, label='demand')
    axs.step(dates, [pe.value(model.p_kauf[k]) for k in  model.steps], label='Energy_Bought')
    axs.step(dates, [pe.value(model.p_bat_Nutz[k]) for k in  model.steps], label='Bat-Use')
    axs.step(dates, [pe.value(model.p_bat_Lade[k]) for k in  model.steps], label='Bat-Charge')
    axs.legend(loc='upper left', fontsize='x-small')
    #axs.set_xlim(lims)
    for label in axs.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('right')
    plt.show()