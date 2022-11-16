import pickle 
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from plotting_functions import load_curve_plot
import datetime as dt

start = '2022-02-08 10:00'
ende = '2022-02-08 11:00'
timeformat = '%Y-%m-%d %H:%M'
day = start[:10]
sol_path = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}'
print(sol_path)
with open(sol_path +'/bat', 'rb') as f:
    bat = pickle.load(f)
with open(sol_path +'/p_bat_Lade', 'rb') as f:
    p_bat_Lade = pickle.load(f)
with open(sol_path +'/p_bat_Nutz', 'rb') as f:
    p_bat_Nutz = pickle.load(f)
with open(sol_path +'/p_einsp', 'rb') as f:
    p_einsp = pickle.load(f)
with open(sol_path +'/p_Nutz', 'rb') as f:
    p_Nutz = pickle.load(f)
with open(sol_path +'/z1', 'rb') as f:
    z1 = pickle.load(f)
delta = int((dt.datetime.strptime(ende, timeformat) - dt.datetime.strptime(start, timeformat)).total_seconds()/60)
dates = [dt.datetime.strptime(start, timeformat) + dt.timedelta(minutes=i) for i in range(delta)]
with open(sol_path +'/prc', 'rb') as f:
    prcspot = pickle.load(f)
with open(sol_path +'/pv', 'rb') as f:
    pvgen = pickle.load(f)
with open(sol_path +'/dmd', 'rb') as f:
    demand = pickle.load(f)
with open(sol_path +'/car', 'rb') as f:
    dcar = pickle.load(f)
with open(sol_path +'/hp', 'rb') as f:
    dhp = pickle.load(f)
with open(sol_path +'/p_kauf', 'rb') as f:
    p_buy = pickle.load(f)

print(bat, "\n", p_bat_Lade, "\n",p_bat_Nutz, "\n",p_einsp, "\n",p_Nutz,"\n", z1,"\n", prcspot, "\n",pvgen, "\n",demand,"\n", dcar,"\n",dhp, "\n",p_buy)

load_curve_plot(dates, prcspot, pvgen, demand, dcar, dhp, p_buy, p_bat_Nutz, p_bat_Lade)