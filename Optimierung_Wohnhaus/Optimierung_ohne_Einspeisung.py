# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 18:18:17 2022

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
    -BatComp1 & BatComp2 -> Laden und Entladen sind komplementär und finden nie gleichzeitig statt
"""


import pyomo.environ as pe
from Datenanalyse.Preprocessing_Functions import dmd, prc, pv, car
#import pandas as pd
#import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

timeformat = '%Y-%m-%d'
timestep = 15
energy_factor = timestep/60

filepath = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/BIblis_15minutes_power.csv'
filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'
Startdatum = '2022-08-01'
Enddatum = '2022-08-02'
delta = (dt.datetime.strptime(Enddatum, timeformat) - dt.datetime.strptime(Startdatum, timeformat)).days * 24 * int(60/timestep)

dmd_biblis = dmd(filepath, Startdatum, Enddatum) 
prc_biblis = prc(filepath_spot, Startdatum, Enddatum)
pv_biblis = pv(filepath, Startdatum, Enddatum)
car_biblis = car(filepath, Startdatum, Enddatum)

C_max = 55000

steps =[i for i in range(delta)]


price_t = dict(zip(steps,prc_biblis))
pv_t = dict(zip(steps,pv_biblis))
d_t = dict(zip(steps,dmd_biblis)) 
dcar_t = dict(zip(steps, car_biblis)) 

model = pe.ConcreteModel()
model.p_kauf = pe.Var(steps, within=pe.NonNegativeReals)
model.p_Nutz = pe.Var(steps, within=pe.NonNegativeReals)
model.p_bat_Nutz = pe.Var(steps, within=pe.NonNegativeIntegers, bounds=(0,energy_factor*C_max))
model.p_bat_Lade = pe.Var(steps, within=pe.NonNegativeIntegers, bounds=(0,energy_factor*C_max))
model.bat = pe.Var(steps, within=pe.NonNegativeIntegers, bounds=(0,C_max))
model.z = pe.Var(steps, within=pe.Binary) 
model.M = 10^5

def ObjCosts(m):  
    return sum(m.p_kauf[t]*price_t[t] for t in steps)
model.obj = pe.Objective(rule=ObjCosts, 
                      sense=pe.minimize)

def SupplyRule(m, t):
    return m.p_Nutz[t] + m.p_bat_Lade[t] <= pv_t[t]
model.SupplyConstr = pe.Constraint(steps, rule=SupplyRule)

#def maxPVGenRule(m, t):
#    return m.p_einsp[t] + m.p_bat_Lade[t] <= pv_t[t]
#model.maxPVGenConstr = pe.Constraint(steps, rule=maxPVGenRule)

def dmdRule(m,t):
    return m.p_kauf[t] + m.p_Nutz[t] + m.p_bat_Nutz[t] >= d_t[t] + dcar_t[t]
model.dmdConstr = pe.Constraint(steps, rule=dmdRule)

def SoCRule(m,t):
    return energy_factor * m.p_bat_Lade[t] <= C_max - m.bat[t]
model.SoCConstr = pe.Constraint(steps, rule=SoCRule)

def UseRule1(m,t):
    return m.p_bat_Nutz[t] <= m.bat[t]
model.UseConstr1 = pe.Constraint(steps, rule=UseRule1)

def UseRule2(m,t):
    return m.p_bat_Nutz[t] <= C_max
model.UseConstr2 = pe.Constraint(steps, rule=UseRule2)

def Bat1(m,t):
    if t >= 1:
        return  m.bat[t] >= m.bat[t-1] + m.p_bat_Lade[t] - m.p_bat_Nutz[t]
    else:
        return m.bat[t] >= 0
model.batConstr1 = pe.Constraint(steps, rule=Bat1)

def Bat2(m,t):
    if t >= 1:
        return  m.bat[t] <= m.bat[t-1] + m.p_bat_Lade[t] - m.p_bat_Nutz[t]
    else:
        return m.bat[t] <= 0
model.batConstr2 = pe.Constraint(steps, rule=Bat2)

def BatComp1(m,t):
    return m.p_bat_Lade[t] <= m.M *m.z[t]
model.BatCompConstr1 = pe.Constraint(steps, rule=BatComp1)

def BatComp2(m,t):
    return m.p_bat_Nutz[t] <= m.M *(1 - m.z[t])
model.BatCompConstr2 = pe.Constraint(steps, rule=BatComp2)


opt = pe.SolverFactory('glpk')
results = opt.solve(model)
results.write()
for t in steps:
    print(pe.value(model.bat[t]), d_t[t], pe.value(model.p_kauf[t]))

battery = [pe.value(model.bat[t]) for t in steps]
fig, axs = plt.subplots()
axs.plot(dmd_biblis, label='demand')
axs.plot(pv_biblis, label='pv')
axs.plot(car_biblis, label='car')
axs.plot(battery, label='bat')