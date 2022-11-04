def scenario_data_generator():
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

    """
    return 

def scenario_structure_generator():
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

    """
    return