import pickle 
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from plotting_functions import load_curve_plot
import datetime as dt

scenarios = [('2022-02-08 10:00', '2022-02-08 11:00'), ('2022-02-09 10:00', '2022-02-09 11:00'), ('2022-02-10 10:00', '2022-02-10 11:00'), ('2022-02-11 10:00', '2022-02-11 11:00'),
             ('2022-02-12 10:00', '2022-02-12 11:00'), ('2022-02-13 10:00', '2022-02-13 11:00'), ('2022-02-14 10:00', '2022-02-14 11:00'), ('2022-02-15 10:00', '2022-02-15 11:00')]

start = scenarios[0][0]
ende = scenarios[0][1]
timeformat = '%Y-%m-%d %H:%M'
day = start[:10]
sc = 'Scenario1'

sol_path_fs = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/FirstStageDecision'
sol_path_scenario = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/{sc}'

with open(sol_path_fs +'/z1', 'rb') as f:
    z1 = pickle.load(f)
with open(sol_path_scenario +'/bat', 'rb') as f:
    bat = pickle.load(f)
with open(sol_path_scenario +'/p_bat_Lade', 'rb') as f:
    p_bat_Lade = pickle.load(f)
with open(sol_path_scenario +'/p_bat_Nutz', 'rb') as f:
    p_bat_Nutz = pickle.load(f)
with open(sol_path_scenario +'/p_einsp', 'rb') as f:
    p_einsp = pickle.load(f)
with open(sol_path_scenario +'/p_Nutz', 'rb') as f:
    p_Nutz = pickle.load(f)
delta = int((dt.datetime.strptime(ende, timeformat) - dt.datetime.strptime(start, timeformat)).total_seconds()/60)
dates = [dt.datetime.strptime(start, timeformat) + dt.timedelta(minutes=i) for i in range(delta)]
with open(sol_path_scenario +'/prc', 'rb') as f:
    prcspot = pickle.load(f)
with open(sol_path_scenario +'/pv', 'rb') as f:
    pvgen = pickle.load(f)
with open(sol_path_scenario +'/dmd', 'rb') as f:
    demand = pickle.load(f)
with open(sol_path_scenario +'/car', 'rb') as f:
    dcar = pickle.load(f)
with open(sol_path_scenario +'/hp', 'rb') as f:
    dhp = pickle.load(f)
with open(sol_path_scenario +'/p_kauf', 'rb') as f:
    p_buy = pickle.load(f)

print(bat, "\n", p_bat_Lade, "\n",p_bat_Nutz, "\n",p_einsp, "\n",p_Nutz,"\n", z1,"\n", prcspot, "\n",pvgen, "\n",demand,"\n", dcar,"\n",dhp, "\n",p_buy)

load_curve_plot(dates, prcspot, pvgen, demand, dcar, dhp, p_buy, p_bat_Nutz, p_bat_Lade)