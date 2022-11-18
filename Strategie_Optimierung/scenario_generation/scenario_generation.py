import sys
import os
sys.path.append('C:/Users/hagem/Optimierung_EMS')
from Preprocessing_Functions import dmd, prc, prc_stretched, pv, car, hp, load_df
import datetime as dt
import numpy as np
import pickle 
filepath = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Biblis/Leistung/Biblis_1minute_power.csv'
filepath_spot = 'C:/Users/hagem/Optimierung_EMS/CSV-Dateien/Spot-Markt Preise 2022/entsoe_spot_germany_2022.csv'

def scenario_data_generator(filepath_prc, filepath_prosumer, scenarios):
    """
    Generiere die Parameterinformationen in einem .dat Format.
    Die Struktur dieser Daten ist immer die folgende:
    ----------------------------------
    # Kommentare werden mit # nicht von der Software eingelesen
    # Werte für ein Beispielszenario mit Indexmenge 'Menge' und zwei Paramtern:
    set Menge := t0 t1 ... ;
    param Parameter1 := t0 Wert1 t1 Wert2 ... ;
    param Einzelwert := EInzelwert;
    ----------------------------------
    -filepath_prc: Dateipfad mit CSV-Datei der Spot-Markt Preise.
    -filepath_prosumer: Dateipfad mit Verbrauch/Erzeugung
    -scenarios: Liste von Szenarien, z.B. Tage, die jeweils als .dat gespeichert werden sollen.
    Annahme: scenarios[0] ist der T 
    """
    scenarionames = []
    timeformat = '%Y-%m-%d %H:%M'
    timestep = 1
    energy_factor = timestep/60
    Startdatum = scenarios[0][0]
    Enddatum = scenarios[0][1]
    day = Startdatum[:10]
    if not os.path.exists(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/'):
        os.makedirs(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/')
    for i in range(len(scenarios)):
        if not os.path.exists(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario' + str(i+1)):
            os.makedirs(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario' + str(i+1))
    delta = int((dt.datetime.strptime(Enddatum, timeformat) - dt.datetime.strptime(Startdatum, timeformat)).total_seconds()/60)
    base = dt.datetime.strptime(Startdatum, timeformat)
    dates = [base + dt.timedelta(minutes=i) for i in range(delta)]
    steps = [f"t{i}" for i in range(delta)]
    prc_biblis = prc(filepath_prc, Startdatum, Enddatum)
    df = load_df(filepath_prosumer)
    if timestep == 1:
        prc_biblis = prc_stretched(prc_biblis)
    for i, bounds in enumerate(scenarios):
        delta = int((dt.datetime.strptime(bounds[1], timeformat) - dt.datetime.strptime(bounds[0], timeformat)).total_seconds()/60)
        base = dt.datetime.strptime(bounds[0], timeformat)
        dates = [base + dt.timedelta(minutes=i) for i in range(delta)]
        dmd_biblis = dmd(df, bounds[0], bounds[1]) 
        pv_biblis = pv(df, bounds[0], bounds[1])
        car_biblis = car(df, bounds[0], bounds[1])
        hp_biblis = hp(df, bounds[0], bounds[1])
        with open(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario{i+1}/dates', 'wb') as f:
            pickle.dump(dates,f)
        with open(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario{i+1}/prc', 'wb') as f:
            pickle.dump(prc_biblis,f)
        dmd_biblis = dmd(df, bounds[0], bounds[1]) 
        with open(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario{i+1}/dmd', 'wb') as f:
            pickle.dump(dmd_biblis,f)
        pv_biblis = pv(df, bounds[0], bounds[1])
        with open(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario{i+1}/pv', 'wb') as f:
            pickle.dump(pv_biblis,f)
        car_biblis = car(df, bounds[0], bounds[1])
        with open(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario{i+1}/car', 'wb') as f:
            pickle.dump(car_biblis,f)
        hp_biblis = hp(df, bounds[0], bounds[1])
        with open(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/results/arrays/{day}/Scenario{i+1}/hp', 'wb') as f:
            pickle.dump(hp_biblis,f)
        with open(f'C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/scenarios/scenario{i+1}.dat', 'w') as f:
            f.write('set steps := ')
            for t in steps:
                f.write(t + " ")
            f.write('; \n')
            f.write('param pv := ')
            for t, value in zip(steps, pv_biblis):
                f.write(f'{t} {value} ')
            f.write('; \n')
            f.write('param d := ')
            for t, value in zip(steps, dmd_biblis):
                f.write(f'{t} {value} ')
            f.write('; \n')
            f.write('param dcar := ')
            for t, value in zip(steps, car_biblis):
                f.write(f'{t} {value} ')
            f.write('; \n')
            f.write('param price := ')
            for t, value in zip(steps, prc_biblis):
                f.write(f'{t} {value} ')
            f.write('; \n')
            f.write('param hp := ')
            for t, value in zip(steps, hp_biblis):
                f.write(f'{t} {value} ')
            f.write('; \n')
            f.write(f'param M := {10**7}; \n')
            f.write(f'param C_max := {200000}; \n')
            f.write(f'param C_Start := {1000}; \n')
        scenarionames.append(f'{i}')
    return scenarionames

def scenario_structure_generator(scenarionames):
    """
    Generiere Informationen über die Szenariostruktur für die stochastische Optimierung.
    Dabei muss das Wissen über die erzeugten Szenarien genutzt werden:
    Das Wissen über die Szenarien wird in Pyomo als Szenariobaum realisiert.
    (Optionale) Parameter die diese Datei beinhaltet sind:
    -Stages: Geordnete Menge mit den Namen aller Zeitschritte, z.B. firstStage, secondStage
    -Nodes: Menge der Name der Knotenpunkte im Szenariobaum
    -NodesStage: Indizierter Parameter der die Node-Namen und die Stage-Namen verknüpft
    -Children: Für jeden Knoten, der kein Blatt ist müssen die Kinder, also verknüpfte Nodes in der nächsten Stufe angegeben werden
    -ConditionalProbability: indizierter Parameter, weist jeder Node eine (bedingte) Wahrscheinlichkeit zu: An den jeweiligen Punktemn muss isch dies zu eins summieren
    -Scenarios: Geordnete Menge mit den Szenarien. Diese müssen mit dem Namen der .dat Dateien übereinstimmen!
    -ScenarioLeafNode: Indizierter Parameter der die Szenarionamen und die Knoten verbindet.
    -StageVariables: Ordnet die Variablen im Optimierungsmodell den Stages zu. (Nichtantizipativität)
    -StageDerivedVariables: wie StageVariables, nur werden diese von anderen Variablen abgeleitet, also antizipativ
    -ScenarioBasedData: boolescher Parameter, Deutet an wie die INstanzen für jedes Szenario konstruiert werden soll. True -> Szenarien in .dat zu finden, False -> Daten in jeweils einer Datei pro Knoten
    -StageCost: Parameter, wird durch die stages indiziert, gibt den Ausdruck für die kOsten in jeder Stufe für das Optimierungsmodell (param StageCost := FirstStage FirstStageCOsta ... ;)
    ---------------------------------
    scnearionames: Liste mit Namen der Scenariodateien .dat, gelistet in Reihenfolge!
    """
    scenario_amount = len(scenarionames)
    probs = [round(1/len(scenarionames), ndigits=5) for scenario in scenarionames]
    if len(probs) > 1:
        probs[1] += (1 - sum(probs)) 
    assert sum(probs) == 1
    with open('C:/Users/hagem/Optimierung_EMS/Strategie_Optimierung/scenarios/ScenarioStructure.dat', 'w') as f:
        f.write('set Stages := FirstStage SecondStage ; \n')
        f.write('set Nodes := RootNode \n')
        for name in scenarionames:
            f.write(f'Node{name} \n')
        f.write('; \n')
        f.write('param NodeStage := RootNode FirstStage \n')
        for name in scenarionames:
            f.write(f"Node{name} SecondStage \n")
        f.write("; \n")
        f.write('set Children[RootNode] := ')
        for name in scenarionames:
            f.write(f'Node{name} \n')
        f.write('; \n')
        f.write("param ConditionalProbability := RootNode 1.0 \n")
        for name, prob in zip(scenarionames, probs):
            f.write(f"Node{name} {prob} \n")
        f.write("; \n")
        f.write("set Scenarios := ")
        for name in scenarionames:
            f.write(f"Scenario{name} \n")
        f.write('; \n')
        f.write("param ScenarioLeafNode := " )
        for name in scenarionames:
            f.write(f"Scenario{name}  Node{name} \n")
        f.write('; \n')
        f.write("set StageVariables[FirstStage] := z1[*]; \n")
        f.write("set StageVariables[SecondStage] := p_kauf[*] \n p_bat_Nutz[*] \n p_bat_Lade[*] \n p_einsp[*] \n bat[*] \n p_Nutz[*]; \n")
        f.write('param StageCost := FirstStage FirstStageCost \n SecondStage SecondStageCost;')
    return

scenarios = [('2022-02-08 10:00', '2022-02-08 11:00'), ('2022-02-09 10:00', '2022-02-09 11:00'), ('2022-02-10 10:00', '2022-02-10 11:00'), ('2022-02-11 10:00', '2022-02-11 11:00'),
             ('2022-02-12 10:00', '2022-02-12 11:00'), ('2022-02-13 10:00', '2022-02-13 11:00'), ('2022-02-14 10:00', '2022-02-14 11:00'), ('2022-02-15 10:00', '2022-02-15 11:00')]
names = scenario_data_generator(filepath_spot,filepath,scenarios)
scenario_structure_generator(names)