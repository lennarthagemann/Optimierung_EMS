import pyomo.environ as pe
from pyomo.util.infeasible import log_infeasible_constraints
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, pv, car, hp, load_df
from plotting_functions import multiscale_load_curve_plot
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.units as munits
import matplotlib.dates as mdates
"""
In diesem Testmodell soll die Optimierung auf zwei Skalen (deterministisch) passieren:
In den ersten 15 Minuten wird minütlich optimiert
In der verbleibenden Zeit wird alle 15 Minuten eine Entscheidung getroffen.
Beispielweise auf einen Tag gesehen: 15 Entscheidungsschritte 1. Phase, 3 + 4*23 = 95 Entscheidungsschritte, insgesamt also 110.
Im Vergleich zum Modell in dem jede Minute optimiert wird: 24*60=1440 Entscheidungsschritte, die Komplexität wird also erheblich minimiert
--> Insbesondere wichtig für das stochastische Optimierungsmodell.
---------------------------------------------------------------------------
1. Lade die Daten für die verschiedenen Skalen ein
2. Rechne die Start und Endpunkte für die Zeitstufen aus anhand des Gesamtzeitraums (also den Mittelpunkt).
3. Teile die Zeitpunkte in zwei Arrays ein: dates1 und dates2 für die zwei Skalen.
4.  1. Möglichkeit: Dupliziere die Variablen und Restriktionen für die jeweiligen zeitlichen Bereiche. (Bessere Möglichkeit, auch wenn viel Redundanz)
    2. Möglichkeit: Packe die Zeitstufen in ein Array, ändere die Restriktionen intern um den Wechsel hinzukriegen. 
5. Löse das Optimierungsmodell
---------------------------------------------------------------------------
"""

def date_splitter(s, e, t, split):
    """
    Löst Stufe 2: Anhand des splits (timedelta-Objekt)wird mittels
    """
    s_dt = dt.datetime.strptime(s, t)
    e_dt = dt.datetime.strptime(e, t)
    m_dt = s_dt + split
    assert m_dt < e_dt
    return m_dt.strftime(t)

timeformat = '%Y-%m-%d %H:%M'
timestep = 1
energy_factor = timestep/60

filepath_1min = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_1minute_power.csv'
filepath_15min = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_15minutes_power.csv'
filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'
Startdatum = '2022-07-25 09:00'
Enddatum = '2022-07-27 10:00'
Mitte = date_splitter(Startdatum, Enddatum, timeformat, dt.timedelta(minutes=15))
delta1 = int((dt.datetime.strptime(Mitte, timeformat) - dt.datetime.strptime(Startdatum, timeformat)).total_seconds()/60)
delta2 = int((dt.datetime.strptime(Enddatum, timeformat) - dt.datetime.strptime(Mitte, timeformat)).total_seconds()/(60*15))

df_1min = load_df(filepath_1min)
dmd_biblis_1min = dmd(df_1min, Startdatum, Enddatum) 
prc_biblis_15min = prc(filepath_spot, Startdatum, Enddatum)
if timestep == 1:
    prc_biblis_1min = prc_stretched(prc_biblis_15min)
pv_biblis_1min = pv(df_1min, Startdatum, Enddatum)
car_biblis_1min = car(df_1min, Startdatum, Enddatum)
hp_biblis_1min = hp(df_1min, Startdatum, Enddatum)

df_15min = load_df(filepath_15min)
dmd_biblis_15min = dmd(df_15min, Startdatum, Enddatum) 
pv_biblis_15min = pv(df_15min, Startdatum, Enddatum)
car_biblis_15min = car(df_15min, Startdatum, Enddatum)
hp_biblis_15min = hp(df_15min, Startdatum, Enddatum)

steps1 = ['t' + str(i) for i in range(delta1)]
steps2 = ['t' + str(i) for i in range(delta2)]
print(steps1, steps2)

"""
-----------------------------------------
1. Zeitskala
-----------------------------------------
"""

model = pe.ConcreteModel()
model.steps1 = pe.Set(initialize=steps1)
price1 = dict(zip(steps1,prc_biblis_1min))
pv1 = dict(zip(steps1,pv_biblis_1min))
d1 = dict(zip(steps1,dmd_biblis_1min)) 
dcar1 = dict(zip(steps1, car_biblis_1min)) 
hp1 = dict(zip(steps1, hp_biblis_1min))
C_max = 150000
C_start = 0
model.p_einsp1 = pe.Var(model.steps1, within=pe.NonNegativeReals)
model.p_kauf1 = pe.Var(model.steps1, within=pe.NonNegativeReals)
model.p_Nutz1 = pe.Var(model.steps1, within=pe.NonNegativeReals)
model.p_bat_Nutz1 = pe.Var(model.steps1, within=pe.NonNegativeReals, bounds=(0,energy_factor*C_max))
model.p_bat_Lade1 = pe.Var(model.steps1, within=pe.NonNegativeReals, bounds=(0,energy_factor*C_max))
model.bat1 = pe.Var(model.steps1, within=pe.NonNegativeReals, bounds=(0,C_max))
model.z1 = pe.Var(model.steps1, within=pe.Binary) 
model.M= 10**5


def ObjCosts1(m):  
    return sum(0.8*m.p_einsp1[t]*price1[t] -m.p_kauf1[t]*price1[t] for t in model.steps1)
model.obj1 = pe.Expression(rule=ObjCosts1)

def SupplyRule1(m, t):
    return m.p_Nutz1[t] + m.p_bat_Lade1[t] + m.p_einsp1[t] <= pv1[t]
model.SupplyConstr1 = pe.Constraint(model.steps1, rule=SupplyRule1)

def maxEinspRule1(m, t):
    return m.p_einsp1[t] <= 0.7*max(pv1.values())
model.maxEinspConstr1 = pe.Constraint(model.steps1, rule=maxEinspRule1)

# def maxPVGenRule1(m, t):
#    return m.p_einsp1[t] + m.p_bat_Lade1[t] <= pv1[t]
# model.maxPVGenConstr1 = pe.Constraint(model.steps1, rule=maxPVGenRule1)

def dmdRule1(m,t):
    return m.p_kauf1[t] + m.p_Nutz1[t] + m.p_bat_Nutz1[t] >= d1[t] + dcar1[t] + hp1[t]
model.dmdConstr1 = pe.Constraint(model.steps1, rule=dmdRule1)

def SoCRule1(m,t):
    if t != model.steps1.first():
        return energy_factor * m.p_bat_Lade1[t] <= C_max - m.bat1[model.steps1.prev(t)]
    else:
        return energy_factor * m.p_bat_Lade1[t] <= C_max - C_start
model.SoCConstr1 = pe.Constraint(model.steps1, rule=SoCRule1)

def UseRule1(m,t):
    if t == model.steps1.first():
        return pe.Constraint.Skip
    else:
        return m.p_bat_Nutz1[t] <= m.bat1[model.steps1.prev(t)]
model.UseConstr1 = pe.Constraint(model.steps1, rule=UseRule1)

def UseDemand1(m,t):
    return m.p_bat_Nutz1[t] <= d1[t] + dcar1[t] + hp1[t]
model.UseDemandConstr1 = pe.Constraint(model.steps1, rule=UseDemand1)

def Bat_lower1(m,t):
    if t != model.steps1.first():
        return m.bat1[t] >= m.bat1[model.steps1.prev(t)] + m.p_bat_Lade1[t] - m.p_bat_Nutz1[t]
    else:
        return m.bat1[t] >= C_start 
model.batConstr_lower1 = pe.Constraint(model.steps1, rule=Bat_lower1)

def Bat_upper1(m,t):
    if t != model.steps1.first():
        return m.bat1[t] <= m.bat1[model.steps1.prev(t)] + m.p_bat_Lade1[t] - m.p_bat_Nutz1[t]
    else:
        return m.bat1[t] <= C_start
model.batConstr_upper1 = pe.Constraint(model.steps1, rule=Bat_upper1)

def BatComp_Lade1(m,t):
    return m.p_bat_Lade1[t] <= m.M *m.z1[t]
model.BatCompConstr_Lade1 = pe.Constraint(model.steps1, rule=BatComp_Lade1)

def BatComp_Nutz1(m,t):
    return m.p_bat_Nutz1[t] <= m.M *(1 - m.z1[t])
model.BatCompConstr_Nutz1 = pe.Constraint(model.steps1, rule=BatComp_Nutz1)


"""
-----------------------------------------
2. Zeitskala
-----------------------------------------
"""
#energy_factor ist dazu da um die Leistung in Energie für die Zeitskalen umzurechnen
energy_factor2 = timestep/4
model.steps2 = pe.Set(initialize=steps2)
price2 = dict(zip(steps2,prc_biblis_15min))
pv2 = dict(zip(steps2,pv_biblis_15min))
d2 = dict(zip(steps2,dmd_biblis_15min)) 
dcar2 = dict(zip(steps2, car_biblis_15min)) 
hp2 = dict(zip(steps2, hp_biblis_15min))
model.p_einsp2 = pe.Var(model.steps2, within=pe.NonNegativeReals)
model.p_kauf2 = pe.Var(model.steps2, within=pe.NonNegativeReals)
model.p_Nutz2 = pe.Var(model.steps2, within=pe.NonNegativeReals)
model.p_bat_Nutz2 = pe.Var(model.steps2, within=pe.NonNegativeReals, bounds=(0,energy_factor*C_max))
model.p_bat_Lade2 = pe.Var(model.steps2, within=pe.NonNegativeReals, bounds=(0,energy_factor*C_max))
model.bat2 = pe.Var(model.steps2, within=pe.NonNegativeReals, bounds=(0,C_max))
model.z2 = pe.Var(model.steps2, within=pe.Binary) 

def ObjCosts2(m):  
    return sum(0.8*m.p_einsp2[t]*price2[t] -m.p_kauf2[t]*price2[t] for t in model.steps2)
model.obj2 = pe.Expression(rule=ObjCosts2)

def SupplyRule2(m, t):
    return m.p_Nutz2[t] + m.p_bat_Lade2[t] + m.p_einsp2[t] <= pv2[t]
model.SupplyConstr2 = pe.Constraint(model.steps2, rule=SupplyRule2)

def maxEinspRule2(m, t):
    return m.p_einsp2[t] <= 0.7*max(pv2.values())
model.maxEinspConstr2 = pe.Constraint(model.steps2, rule=maxEinspRule2)

# def maxPVGenRule2(m, t):
#    return m.p_einsp2[t] + m.p_bat_Lade2[t] <= pv2[t]
# model.maxPVGenConstr2 = pe.Constraint(model.steps2, rule=maxPVGenRule2)

def dmdRule2(m,t):
    return m.p_kauf2[t] + m.p_Nutz2[t] + m.p_bat_Nutz2[t] >= d2[t] + dcar2[t] + hp2[t]
model.dmdConstr2 = pe.Constraint(model.steps2, rule=dmdRule2)

def SoCRule2(m,t):
    if t == model.steps2.first():
        return energy_factor * m.p_bat_Lade2[t] <= C_max - m.bat1[model.steps1.last()]
    else:
        return energy_factor * m.p_bat_Lade2[t] <= C_max - m.bat2[model.steps2.prev(t)]
model.SoCConstr1 = pe.Constraint(model.steps2, rule=SoCRule2)

def UseRule2(m,t):
    if t==model.steps2.first():
        return m.p_bat_Nutz2[t] <= m.bat1[model.steps1.last()]
    else:
        return m.p_bat_Nutz2[t] <= m.bat2[model.steps2.prev(t)]
model.UseConstr2 = pe.Constraint(model.steps2, rule=UseRule2)

def UseDemand2(m,t):
    return m.p_bat_Nutz2[t] <= d2[t] + dcar2[t] + hp2[t]
model.UseDemandConstr2 = pe.Constraint(model.steps2, rule=UseDemand2)

def Bat_lower2(m,t):
    if t==model.steps2.first():
        return m.bat2[t] >= m.bat1[m.steps1.last()]
    else:
        return m.bat2[t] >= m.bat2[model.steps2.prev(t)] + m.p_bat_Lade2[t] - m.p_bat_Nutz2[t]
model.batConstr_lower2 = pe.Constraint(model.steps2, rule=Bat_lower2)

def Bat_upper2(m,t):
    if t==model.steps2.first():
        return m.bat2[t] <= m.bat1[m.steps1.last()]  
    else:
        return m.bat2[t] <= m.bat2[model.steps2.prev(t)] + m.p_bat_Lade2[t] - m.p_bat_Nutz2[t]
model.batConstr_upper2 = pe.Constraint(model.steps2, rule=Bat_upper2)

def BatComp_Lade2(m,t):
    return m.p_bat_Lade2[t] <= m.M *m.z2[t]
model.BatCompConstr_Lade2 = pe.Constraint(model.steps2, rule=BatComp_Lade2)

def BatComp_Nutz2(m,t):
    return m.p_bat_Nutz2[t] <= m.M *(1 - m.z2[t])
model.BatCompConstr_Nutz2 = pe.Constraint(model.steps2, rule=BatComp_Nutz2)

"""
-----------------------------------------
Zielfunktion bestimmen, lösen und plotten
-----------------------------------------
"""

def TotalObjCosts(m):
    return m.obj1 + m.obj2
model.obj = pe.Objective(rule=TotalObjCosts, 
                      sense=pe.maximize)

results = pe.SolverFactory('glpk').solve(model, tee=True)
model.display()

print([pe.value(model.bat1[k]) for k in model.steps1])
print([pe.value(model.bat2[k]) for k in model.steps2])

multiscale_load_curve_plot(steps1, [5000* i for i in list(price1.values())], list(pv1.values()), list(d1.values()), list(dcar1.values()), list(hp1.values()),
                 [pe.value(model.p_kauf1[k]) for k in  model.steps1], 
                [pe.value(model.p_bat_Nutz1[k]) for k in  model.steps1], 
                [pe.value(model.p_bat_Lade1[k]) for k in  model.steps1],
                steps2, [5000*i for i in list(price2.values())], list(pv2.values()), list(d2.values()), list(dcar2.values()), list(hp2.values()), 
                [pe.value(model.p_kauf2[k]) for k in  model.steps2], 
                [pe.value(model.p_bat_Nutz2[k]) for k in  model.steps2], 
                [pe.value(model.p_bat_Lade2[k]) for k in  model.steps2])