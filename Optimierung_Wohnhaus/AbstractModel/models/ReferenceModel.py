import pyomo.environ as pe
from Datenanalyse.Preprocessing_Functions import dmd, prc, prc_stretched, pv, car
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.units as munits
import matplotlib.dates as mdates

model = pe.AbstractModel()


def ObjCosts(m):  
    return sum(0.8*m.p_einsp[t]*price_t[t] -m.p_kauf[t]*price_t[t] for t in steps)
model.obj = pe.Objective(rule=ObjCosts, 
                      sense=pe.maximize)

def SupplyRule(m, t):
    return m.p_Nutz[t] + m.p_bat_Lade[t] + m.p_einsp[t] <= pv_t[t]
model.SupplyConstr = pe.Constraint(steps, rule=SupplyRule)

def maxEinspRule(m, t):
    return m.p_einsp[t] <= 0.7*max(pv_t.values())
model.maxEinspConstr = pe.Constraint(steps, rule=maxEinspRule)

def maxPVGenRule(m, t):
   return m.p_einsp[t] + m.p_bat_Lade[t] <= pv_t[t]
model.maxPVGenConstr = pe.Constraint(steps, rule=maxPVGenRule)

def dmdRule(m,t):
    return m.p_kauf[t] + m.p_Nutz[t] + m.p_bat_Nutz[t] >= d[t] + dcar[t]
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
    return m.p_bat_Lade[t] <= m.M *m.z1[t]
model.BatCompConstr1 = pe.Constraint(steps, rule=BatComp1)

def BatComp2(m,t):
    return m.p_bat_Nutz[t] <= m.M *(1 - m.z1[t])
model.BatCompConstr2 = pe.Constraint(steps, rule=BatComp2)

def buyRule(m,t):
    return m.p_kauf[t] <= d[t] + dcar[t]
model.buyConstr = pe.Constraint(steps, rule=buyRule)

pe.SolverFactory('glpk').solve(model, tee=True)
with open('variable.txt', 'w') as f:
    model.pprint(ostream=f)