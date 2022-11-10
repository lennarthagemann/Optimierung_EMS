# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 18:35:43 2022

@author: hagem
"""

"""
Ziel: Optimierung eines einzelnen Tages basierend auf Szenarien
Zielfunktion(ObjCosts): Basiert auf den Kosten zu jeder Zeitstufe: Wie viel Strom kaufen wir zur Bedarfsdeckung,
wie viel können wir zu welchem Preis einspeisen.
Restriktionen: Technische Restriktionen und Wunschrestriktionen, z.B. je nach
SoC sofort laden wenn E-Auto ankommt. Der Ladestand der Batterie muss aus den Entscheidungen der 
letzten Stufe hervorgehen, und muss innerhalb der technische Grenzen bleiben

--------------------------
Variablen:
    -p_einsp -> Strom der eingespeist wird zu jedem Zeitpunkt
    -p_kauf -> Strom der eingekauft werden muss, z.B. um Bedarf zu decken
    -p_Bat -> Strom der aus der Batterie bezogen wird
--------------------------
Restriktionen:
    -maxEinspRule -> Die Anlage darf nur einen bestimmten Teil ihrer Maximalleistung zu jedem Zeitpunkt einspeisen 
    -maxPVEinso -> Man kann nicht mehr einspeisen als 
    -dmdRule -> Gekaufter Strom und erzeugter Strom müssen Bedarf decken
    -Bat1 & Bat2 -> Implizieren die Ladung der Batterie in der nächste Stufe durch Einspeisung & Verbrauch
    buyRule -> Wir können nicht mehr einkaufen als wir maximal benötigen um unseren Verbrauch zu decken
                Ansonsten würden wir unendlich viel kaufen und Geld verdienen falls der SPotpreis negativ ist

"""


import pyomo.environ as pe
from pyomo.util.infeasible import log_infeasible_constraints
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, pv, car, hp, load_df, moving_average
from plotting_functions import load_curve_plot
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.units as munits
import matplotlib.dates as mdates

timeformat = '%Y-%m-%d %H:%M'
timestep = 1
energy_factor = timestep/60
smth=True

filepath = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_1minute_power.csv'
filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'
Startdatum = '2022-05-08 00:00'
Enddatum = '2022-05-09 00:00'
delta = int((dt.datetime.strptime(Enddatum, timeformat) - dt.datetime.strptime(Startdatum, timeformat)).total_seconds()/60)

df = load_df(filepath)
dmd_biblis = dmd(df, Startdatum, Enddatum, smooth=smth) 
prc_biblis = prc(filepath_spot, Startdatum, Enddatum)
if timestep == 1:
    prc_biblis = prc_stretched(prc_biblis)
pv_biblis = pv(df, Startdatum, Enddatum, smooth=smth)
car_biblis = car(df, Startdatum, Enddatum, smooth=smth)
hp_biblis = hp(df, Startdatum, Enddatum, smooth=smth)



steps = [i for i in range(delta)]

model = pe.ConcreteModel()
model.steps = pe.Set(initialize=steps)
price = dict(zip(steps,prc_biblis))
pv = dict(zip(steps,pv_biblis))
d = dict(zip(steps,dmd_biblis)) 
dcar = dict(zip(steps, car_biblis)) 
hp = dict(zip(steps, hp_biblis))
C_max = 200000
C_start = 0
model.p_einsp = pe.Var(model.steps, within=pe.NonNegativeReals)
model.p_kauf = pe.Var(model.steps, within=pe.NonNegativeReals)
model.p_Nutz = pe.Var(model.steps, within=pe.NonNegativeReals)
model.p_bat_Nutz = pe.Var(model.steps, within=pe.NonNegativeReals, bounds=(0,energy_factor*C_max))
model.p_bat_Lade = pe.Var(model.steps, within=pe.NonNegativeReals, bounds=(0,energy_factor*C_max))
model.bat = pe.Var(model.steps, within=pe.NonNegativeReals, bounds=(0,C_max))
model.z1 = pe.Var(model.steps, within=pe.Binary) 
model.M = 10**5

def ObjCosts(m):  
    return sum(0.8*m.p_einsp[t]*price[t] -m.p_kauf[t]*price[t] for t in model.steps)
model.obj = pe.Objective(rule=ObjCosts, 
                      sense=pe.maximize)

def SupplyRule(m, t):
    return m.p_Nutz[t] + m.p_bat_Lade[t] + m.p_einsp[t] <= pv[t]
model.SupplyConstr = pe.Constraint(model.steps, rule=SupplyRule)

def maxEinspRule(m, t):
    return m.p_einsp[t] <= 0.7*max(pv.values())
model.maxEinspConstr = pe.Constraint(model.steps, rule=maxEinspRule)

def maxPVGenRule(m, t):
   return m.p_einsp[t] + m.p_bat_Lade[t] <= pv[t]
model.maxPVGenConstr = pe.Constraint(model.steps, rule=maxPVGenRule)

def dmdRule(m,t):
    return m.p_kauf[t] + m.p_Nutz[t] + m.p_bat_Nutz[t] >= d[t] + dcar[t] + hp[t]
model.dmdConstr = pe.Constraint(model.steps, rule=dmdRule)

def SoCRule(m,t):
    if t >= 1:
        return energy_factor * m.p_bat_Lade[t] <= C_max - m.bat[t-1]
    else:
        return energy_factor * m.p_bat_Lade[t] <= C_max - C_start
model.SoCConstr = pe.Constraint(model.steps, rule=SoCRule)

def UseRule1(m,t):
    if t==0:
        return pe.Constraint.Skip
    else:
        return m.p_bat_Nutz[t] <= m.bat[t-1]
model.UseConstr1 = pe.Constraint(model.steps, rule=UseRule1)

# def UseRule2(m,t):
#     return m.p_bat_Nutz[t] <= C_max
# model.UseConstr2 = pe.Constraint(model.steps, rule=UseRule2)

def UseDemand(m,t):
    return m.p_bat_Nutz[t] <= d[t] + dcar[t] + hp[t]
model.UseDemandConstr = pe.Constraint(model.steps, rule=UseDemand)

def Bat1(m,t):
    if t >= 1:
        return  m.bat[t] >= m.bat[t-1] + m.p_bat_Lade[t] - m.p_bat_Nutz[t]
    else:
        return m.bat[t] >= C_start
model.batConstr1 = pe.Constraint(model.steps, rule=Bat1)

def Bat2(m,t):
    if t >= 1:
        return  m.bat[t] <= m.bat[t-1] + m.p_bat_Lade[t] - m.p_bat_Nutz[t]
    else:
        return m.bat[t] <= C_start
model.batConstr2 = pe.Constraint(model.steps, rule=Bat2)

def BatComp1(m,t):
    return m.p_bat_Lade[t] <= m.M *m.z1[t]
model.BatCompConstr1 = pe.Constraint(model.steps, rule=BatComp1)

def BatComp2(m,t):
    return m.p_bat_Nutz[t] <= m.M *(1 - m.z1[t])
model.BatCompConstr2 = pe.Constraint(model.steps, rule=BatComp2)

def buyRule(m,t):
    return m.p_kauf[t] <= d[t] + dcar[t] + hp[t]
model.buyConstr = pe.Constraint(model.steps, rule=buyRule)

pe.SolverFactory('glpk').solve(model, tee=True)
log_infeasible_constraints(model)
# with open('variable.txt', 'w') as f:
#     model.pprint(ostream=f)
base = dt.datetime.strptime(Startdatum, timeformat)
#lims = (dt.datetime.strptime(Startdatum, timeformat), dt.datetime.strptime(Enddatum, timeformat))
dates = [base + dt.timedelta(minutes=i) for i in range(delta)]

#converter = mdates.ConciseDateConverter()
#munits.registry[dt.datetime] = converter

load_curve_plot(dates, prc_biblis, pv_biblis, dmd_biblis, car_biblis, hp_biblis, [pe.value(model.p_kauf[k]) for k in  model.steps], 
                [pe.value(model.p_bat_Nutz[k]) for k in  model.steps], 
                [pe.value(model.p_bat_Lade[k]) for k in  model.steps])

# fig, axs = plt.subplots(constrained_layout=True)
# axs.step(dates, 5000*prc_biblis, label='price', alpha=0.3)
# axs.step(dates, pv_biblis, label='pv')
# axs.step(dates, dmd_biblis + car_biblis + hp_biblis, label='demand')
# axs.step(dates, [pe.value(model.p_kauf[k]) for k in  model.steps], label='Energy_Bought')
# axs.step(dates, [pe.value(model.p_bat_Nutz[k]) for k in  model.steps], label='Bat-Use')
# axs.step(dates, [pe.value(model.p_bat_Lade[k]) for k in  model.steps], label='Bat-Charge')
# axs.legend(loc='upper left', fontsize='x-small')
# #axs.set_xlim(lims)
# for label in axs.get_xticklabels():
#     label.set_rotation(30)
#     label.set_horizontalalignment('right')
# plt.show()