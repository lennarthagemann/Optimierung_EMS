import json 
import os
import shutil
from itertools import groupby
import re
import pickle 
"""
-------------------------------------
Lade die Lösung im JSON-Format in Numpy Arrays, um diese nachher vernünftig zu visualisieren.
Problem: Zeitstufen der Variablen wurden als eigenständige variablen abgespeichert.
    1. Zip Lösungen und Variablen zusammen in Tupel
    2. Gruppiere Tupel anhand Variablen mit regulärem Ausdruck
    3. Für alle Szenarien (also alle Nodes) lese die Lösung aus
    4. Speichere Lösungen in Array, speichere anhand des Namens der regex
    5. Speichere einzelne Arrays mittels der Namen in results/Zeitraum/ScenarioX/Arrays (X Zahl des Szenarios)
-------------------------------------
"""

def lex_to_num_sorter(dict):
    """
    Sortiere ein Dictionary mit keys der Form (Variablenname)[t(number)]. 
    """
    return {t : dict[t] for t in sorted(dict , key=lambda x: int(x.split('[t')[1].split(']')[0]))}

method='ph'
day = "2022-08-01"

sc_count = 16
Scenarios = [j for j in range(sc_count)]
src = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/{method}_solution.json'
dest = f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/{method}_solution.json'
shutil.move(src, dest)
save_dest = 'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/' + day
if not os.path.exists(save_dest):
    os.makedirs(save_dest)

patterns_1s = ['z1\[\w\d+\]', 'z2\[\w\d+\]']
patterns_2s = ['p_kauf\[\w\d+\]','bat\[\w\d+\]', 'p_Nutz\[\w\d+\]', 'p_bat_Lade\[\w\d+\]', 'p_bat_Nutz\[\w\d+\]', 'p_einsp\[\w\d+\]']
expr = '\[\w\d+\]'
with open(f'results/arrays/{day}/{method}_solution.json', 'r') as f:
    results = json.load(f)
    args = [j  for j in results["node solutions"]["RootNode"]["variables"]]
    vals = [results["node solutions"]["RootNode"]["variables"][j]["solution"] for j in results["node solutions"]["RootNode"]["variables"]]
    solution_set = lex_to_num_sorter(dict(zip(args, vals)))
    for pat in patterns_1s:
        temp = {}
        for sol in solution_set.items():
            matches = re.finditer(pat, sol[0])
            for match in matches:
                temp.update({match.group(0) : solution_set[match.group(0)]})
        temp = lex_to_num_sorter(temp)
        print(temp)
        if not os.path.exists(save_dest + "/FirstStageDecision"):
            os.makedirs(save_dest  + "/FirstStageDecision")
        with open(save_dest + "/FirstStageDecision/" + pat.rstrip(expr), 'wb') as s:
            pickle.dump(list(temp.values()), s) 
    for sc in Scenarios:
        args_2s = [j  for j in results["node solutions"][f"Node{sc}"]["variables"]]
        vals_2s = [results["node solutions"][f"Node{sc}"]["variables"][j]["solution"] for j in results["node solutions"][f"Node{sc}"]["variables"]]
        solution_set_2s = lex_to_num_sorter(dict(zip(args_2s, vals_2s)))
        for pat in patterns_2s:
            temp_2s = {}
            for sol in solution_set_2s.items():
                matches_2s = re.finditer(pat, sol[0])
                for match in matches_2s:
                    temp_2s.update({match.group(0) : solution_set_2s[match.group(0)]})
            temp_2s = lex_to_num_sorter(temp_2s)
            print(temp_2s)
            scenario_savedest = save_dest + "/" + f'Scenario{sc}'
            if not os.path.exists(scenario_savedest):
                os.makedirs(scenario_savedest)
            with open(scenario_savedest + "/" + pat.rstrip(expr), 'wb') as s:
                pickle.dump(list(temp_2s.values()), s) 