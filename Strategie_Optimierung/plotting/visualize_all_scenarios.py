import pickle 
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from plotting_functions import load_curve_plot, all_scenarios_load_curve_plot
import datetime as dt

hours = (' 00:00', ' 00:00')
month = '08'
year = '2022'
days = ['0' + str(i) if (i < 10) else str(i) for i in range(1,18)]
days = [f'{year}-{month}-{day}' for day in days]
scenarios = [(day + hours[0], day + hours[1]) for day in days]

scenarios = [(days[i] + hours[0], days[i+1]  + hours[1]) for i in range(len(days)-1)]

start = scenarios[0][0]
ende = scenarios[0][1]
timeformat = '%Y-%m-%d %H:%M'
day = start[:10]
sol_path_fs = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/FirstStageDecision'
sol_path_scenario = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario'

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
    with open(sol_path_scenario + str(i) + '/bat', 'rb') as f:
        bat = pickle.load(f)
    bat_arr.append(bat)
    with open(sol_path_scenario + str(i) +'/p_bat_Lade', 'rb') as f:
        p_bat_Lade = pickle.load(f)
    p_bat_Lade_arr.append(p_bat_Lade)
    with open(sol_path_scenario + str(i) +'/p_bat_Nutz', 'rb') as f:
        p_bat_Nutz = pickle.load(f)
    p_bat_Nutz_arr.append(p_bat_Nutz)
    with open(sol_path_scenario + str(i) +'/p_einsp', 'rb') as f:
        p_einsp = pickle.load(f)
    p_einsp_arr.append(p_einsp)
    with open(sol_path_scenario + str(i) +'/p_Nutz', 'rb') as f:
        p_Nutz = pickle.load(f)
    p_Nutz_arr.append(p_Nutz)
    with open(sol_path_scenario + str(i) +'/pv', 'rb') as f:
        pvgen = pickle.load(f)
    pv_arr.append(pvgen)
    with open(sol_path_scenario + str(i) +'/dmd', 'rb') as f:
        demand = pickle.load(f)
    dmd_arr.append(demand)
    with open(sol_path_scenario + str(i) +'/car', 'rb') as f:
        dcar = pickle.load(f)
    car_arr.append(dcar)
    with open(sol_path_scenario + str(i) +'/hp', 'rb') as f:
        dhp = pickle.load(f)
    hp_arr.append(dhp)
    with open(sol_path_scenario + str(i) +'/p_kauf', 'rb') as f:
        p_kauf = pickle.load(f)
    p_kauf_arr.append(p_kauf)
    with open(sol_path_scenario + str(i) +'/dates', 'rb') as f:
        dates = pickle.load(f)
    dates_arr.append(dates)


#load_curve_plot(dates_arr[0], prcspot, pv_arr[0], dmd_arr[0], car_arr[0], hp_arr[0], p_kauf_arr[0], p_bat_Nutz_arr[0], p_bat_Lade_arr[0])
all_scenarios_load_curve_plot(4, 4, dates_arr, prcspot, pv_arr, dmd_arr, car_arr, hp_arr, p_kauf_arr, p_bat_Nutz_arr, p_bat_Lade_arr)