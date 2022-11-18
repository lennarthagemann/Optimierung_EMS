import pickle 
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from plotting_functions import load_curve_plot, all_scenarios_load_curve_plot
import datetime as dt


scenarios = [('2022-02-08 10:00', '2022-02-08 11:00'), ('2022-02-09 10:00', '2022-02-09 11:00'), ('2022-02-10 10:00', '2022-02-10 11:00'), ('2022-02-11 10:00', '2022-02-11 11:00'),
             ('2022-02-12 10:00', '2022-02-12 11:00'), ('2022-02-13 10:00', '2022-02-13 11:00'), ('2022-02-14 10:00', '2022-02-14 11:00'), ('2022-02-15 10:00', '2022-02-15 11:00')]

start = scenarios[0][0]
ende = scenarios[0][1]
timeformat = '%Y-%m-%d %H:%M'
day = start[:10]
sol_path_fs = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/FirstStageDecision'
sol_path_scenario = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario'
print(sol_path_scenario)
bat_arr = []
p_bat_Lade_arr = []
p_bat_Nutz_arr = []
p_einsp_arr = []
p_Nutz_arr = []
pv_arr = []
dmd_arr = []
car_arr = []
hp_arr = []
p_kauf_arr =[]
dates_arr = []

with open(sol_path_scenario + '1/prc', 'rb') as f:
    prcspot = pickle.load(f)
with open(sol_path_fs +'/z1', 'rb') as f:
    z1 = pickle.load(f)

for i, sc in enumerate(scenarios):
    with open(sol_path_scenario + str(i+1) + '/bat', 'rb') as f:
        bat = pickle.load(f)
    bat_arr.append(bat)
    with open(sol_path_scenario + str(i+1) +'/p_bat_Lade', 'rb') as f:
        p_bat_Lade = pickle.load(f)
    p_bat_Lade_arr.append(p_bat_Lade)
    with open(sol_path_scenario + str(i+1) +'/p_bat_Nutz', 'rb') as f:
        p_bat_Nutz = pickle.load(f)
    p_bat_Nutz_arr.append(p_bat_Nutz)
    with open(sol_path_scenario + str(i+1) +'/p_einsp', 'rb') as f:
        p_einsp = pickle.load(f)
    p_einsp_arr.append(p_einsp)
    with open(sol_path_scenario + str(i+1) +'/p_Nutz', 'rb') as f:
        p_Nutz = pickle.load(f)
    p_Nutz_arr.append(p_Nutz)
    with open(sol_path_scenario + str(i+1) +'/pv', 'rb') as f:
        pvgen = pickle.load(f)
    pv_arr.append(pvgen)
    with open(sol_path_scenario + str(i+1) +'/dmd', 'rb') as f:
        demand = pickle.load(f)
    dmd_arr.append(demand)
    with open(sol_path_scenario + str(i+1) +'/car', 'rb') as f:
        dcar = pickle.load(f)
    car_arr.append(dcar)
    with open(sol_path_scenario + str(i+1) +'/hp', 'rb') as f:
        dhp = pickle.load(f)
    hp_arr.append(dhp)
    with open(sol_path_scenario + str(i+1) +'/p_kauf', 'rb') as f:
        p_kauf = pickle.load(f)
    p_kauf_arr.append(p_kauf)
    with open(sol_path_scenario + str(i+1) +'/dates', 'rb') as f:
        dates = pickle.load(f)
    dates_arr.append(dates)
print(bat_arr, "\n", p_bat_Lade_arr, "\n",p_bat_Nutz_arr, "\n",p_einsp_arr, "\n",p_Nutz_arr,"\n", z1,"\n", prcspot, 
"\n",pv_arr, "\n",dmd_arr,"\n", car_arr,"\n",hp_arr, "\n",p_kauf_arr)

#load_curve_plot(dates_arr[0], prcspot, pv_arr[0], dmd_arr[0], car_arr[0], hp_arr[0], p_kauf_arr[0], p_bat_Nutz_arr[0], p_bat_Lade_arr[0])
all_scenarios_load_curve_plot(4, 2, dates_arr, prcspot, pv_arr, dmd_arr, car_arr, hp_arr, p_kauf_arr, p_bat_Nutz_arr, p_bat_Lade_arr)