import pickle 
import sys
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from plotting_functions import load_curve_plot, all_scenarios_load_curve_plot
import datetime as dt

scenario_count = 6
scenarios = [i for i in range(scenario_count)]
sol_path_fs = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/Samples/FirstStageDecision'
sol_path_scenario = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/Samples'

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
dates_arr = [] #Relikt von voriger Szenariogeneration aus verschiedenen Tagen, wähle einen x-beliebigen Tag und dupliziere ihn je nach Anzahl der Szenarien

with open(sol_path_scenario + f'/prc/prc', 'rb') as f:
    prcspot = pickle.load(f)
with open(sol_path_fs +'/z1', 'rb') as f:
    z1 = pickle.load(f)

for i, sc in enumerate(scenarios):
    with open(sol_path_scenario + f'/Scenario{i}' + '/bat', 'rb') as f:
        bat = pickle.load(f)
    bat_arr.append(bat)
    with open(sol_path_scenario + f'/Scenario{i}' +'/p_bat_Lade', 'rb') as f:
        p_bat_Lade = pickle.load(f)
    p_bat_Lade_arr.append(p_bat_Lade)
    with open(sol_path_scenario + f'/Scenario{i}' +'/p_bat_Nutz', 'rb') as f:
        p_bat_Nutz = pickle.load(f)
    p_bat_Nutz_arr.append(p_bat_Nutz)
    with open(sol_path_scenario + f'/Scenario{i}' +'/p_einsp', 'rb') as f:
        p_einsp = pickle.load(f)
    p_einsp_arr.append(p_einsp)
    with open(sol_path_scenario + f'/Scenario{i}' +'/p_Nutz', 'rb') as f:
        p_Nutz = pickle.load(f)
    p_Nutz_arr.append(p_Nutz)
    with open(sol_path_scenario + f'/Scenario{i}' +'/p_kauf', 'rb') as f:
        p_kauf = pickle.load(f)
    p_kauf_arr.append(p_kauf)
    # Die parametrischen Daten aus der Szenariogeneration (keine Entscheidungsvariablen) wurden leicht ander sabgespeichert und müssen anders geladen werden
    with open(sol_path_scenario + f'/pv/pv_{i}', 'rb') as f:
        pvgen = pickle.load(f)
    pv_arr.append(pvgen)
    with open(sol_path_scenario + f'/dmd/dmd_{i}', 'rb') as f:
        demand = pickle.load(f)
    dmd_arr.append(demand)
    with open(sol_path_scenario + f'/car/car_{i}', 'rb') as f:
        dcar = pickle.load(f)
    car_arr.append(dcar)
    with open(sol_path_scenario + f'/hp/hp_{i}', 'rb') as f:
        dhp = pickle.load(f)
    hp_arr.append(dhp)


dates_arr = [[dt.datetime(2022,12,15,0,0) + dt.timedelta(minutes=i*15) for i in range(96)] for j in range(scenario_count)]

index=5
load_curve_plot(dates_arr[index], prcspot, pv_arr[index], dmd_arr[index], car_arr[index], hp_arr[index], p_kauf_arr[index], p_bat_Nutz_arr[index], p_bat_Lade_arr[index])
all_scenarios_load_curve_plot(3, 3, dates_arr, prcspot, pv_arr, dmd_arr, car_arr, hp_arr, p_kauf_arr, p_bat_Nutz_arr, p_bat_Lade_arr)