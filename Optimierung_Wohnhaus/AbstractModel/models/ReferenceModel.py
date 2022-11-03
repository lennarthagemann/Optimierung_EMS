import pyomo.environ as pe
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, pv, car
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.units as munits
import matplotlib.dates as mdates

timeformat = '%Y-%m-%d %H:%M'
timestep = 1
energy_factor = timestep/60

model = pe.AbstractModel(name='(Biblis1)')
model.steps = pe.Set()
model.price = pe.Param(model.steps, within=pe.Reals)
model.pv = pe.Param(model.steps, within=pe.NonNegativeReals)
model.d = pe.Param(model.steps, within=pe.NonNegativeReals)
model.dcar = pe.Param(model.steps, within=pe.NonNegativeReals)
model.M = pe.Param(within=pe.NonNegativeIntegers)
model.C_max = pe.Param(within=pe.NonNegativeIntegers)
model.p_einsp = pe.Var(model.steps, within=pe.NonNegativeReals)
model.p_kauf = pe.Var(model.steps, within=pe.NonNegativeReals)
model.p_Nutz = pe.Var(model.steps, within=pe.NonNegativeReals)
model.p_bat_Nutz = pe.Var(model.steps, within=pe.NonNegativeReals, bounds=(0,energy_factor*model.C_max))
model.p_bat_Lade = pe.Var(model.steps, within=pe.NonNegativeReals, bounds=(0,energy_factor*model.C_max))
model.bat = pe.Var(model.steps, within=pe.NonNegativeReals, bounds=(0,model.C_max))
model.z1 = pe.Var(model.steps, within=pe.Binary) 

def ObjCosts(m):  
    return sum(0.8*m.p_einsp[t]*m.price[t] -m.p_kauf[t]*m.price[t] for t in m.steps)
model.obj = pe.Objective(rule=ObjCosts, 
                      sense=pe.maximize)

def SupplyRule(m, t):
    return m.p_Nutz[t] + m.p_bat_Lade[t] + m.p_einsp[t] <= m.pv[t]
model.SupplyConstr = pe.Constraint(model.steps, rule=SupplyRule)

def maxEinspRule(m, t):
    return m.p_einsp[t] <= 0.7*max(m.pv.values())
model.maxEinspConstr = pe.Constraint(model.steps, rule=maxEinspRule)

def maxPVGenRule(m, t):
   return m.p_einsp[t] + m.p_bat_Lade[t] <= m.pv[t]
model.maxPVGenConstr = pe.Constraint(model.steps, rule=maxPVGenRule)

def dmdRule(m,t):
    return m.p_kauf[t] + m.p_Nutz[t] + m.p_bat_Nutz[t] >= m.d[t] + m.dcar[t]
model.dmdConstr = pe.Constraint(model.steps, rule=dmdRule)

def SoCRule(m,t):
    return energy_factor * m.p_bat_Lade[t] <= m.C_max - m.bat[t]
model.SoCConstr = pe.Constraint(model.steps, rule=SoCRule)

def UseRule1(m,t):
    if t==m.steps.first():
        return pe.Constraint.Skip
    else:
        return m.p_bat_Nutz[t] <= m.bat[m.steps.prev(t)]
model.UseConstr1 = pe.Constraint(model.steps, rule=UseRule1)

def UseDemand(m,t):
    return m.p_bat_Nutz[t] <= m.d[t] + m.dcar[t]
model.UseDemandConstr = pe.Constraint(model.steps, rule=UseDemand)

def Bat1(m,t):
    if t !='t0':
        return  m.bat[t] >= m.bat[m.steps.prev(t)] + m.p_bat_Lade[t] - m.p_bat_Nutz[t]
    else:
        return m.bat[t] >= 0
model.batConstr1 = pe.Constraint(model.steps, rule=Bat1)

def Bat2(m,t):
    if t != 't0':
        return  m.bat[t] <= m.bat[m.steps.prev(t)] + m.p_bat_Lade[t] - m.p_bat_Nutz[t]
    else:
        return m.bat[t] <= 0
model.batConstr2 = pe.Constraint(model.steps, rule=Bat2)

def BatComp1(m,t):
    return m.p_bat_Lade[t] <= m.M *m.z1[t]
model.BatCompConstr1 = pe.Constraint(model.steps, rule=BatComp1)

def BatComp2(m,t):
    return m.p_bat_Nutz[t] <= m.M *(1 - m.z1[t])
model.BatCompConstr2 = pe.Constraint(model.steps, rule=BatComp2)

def buyRule(m,t):
    return m.p_kauf[t] <= m.d[t] + m.dcar[t]
model.buyConstr = pe.Constraint(model.steps, rule=buyRule)

# opt = pe.SolverFactory('glpk')
# instance = model.create_instance("C:/Users/hagem/Optimierung_EMS/Optimierung_Wohnhaus/AbstractModel/scenarios/scenario.dat")
# results = opt.solve(instance)

# with open('variable.txt', 'w') as f:
#     model.pprint(ostream=f)