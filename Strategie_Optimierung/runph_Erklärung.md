# runph

Diese Lösungsstrategie basiert auf dem **Progressiven Hedging** zur Dekomposition.
Da das Problem möglicherweise viele Szenarien hat und eine  große Anzahl binärer Variablen in der 
ersten Stufe, ist es effizient lösbar mit Schnittebenenstrategien. Das
`runef` Kommando ist nicht mehr ausreichend, da die erweiterte Form zu groß wird.
Die Idee des Algorithmus ist wie folgt:
1. Für jedes Szenario s löse das deterministische Optimierungsproblem 
2. Eine vermutlich nicht zulässige Lösung wird durch Mittelwertbildung über alle Szenarien an allen Knotenpunkten ermittelt
3. Optimiere erneut wie in Schritt 1, bestrafe nun aber die Unzulässigkeit mit einem approximierten Subgradienten für die Nichtantizipativität und einem quadratischen Fehlerterm für die Abweichung vond er Szenariolösung von Mittelwertlösung
4. Falls Konvergenz unzureichend, sonstige Abbruchbedingungen nicht erfüllt sind, gehe zu Schritt 2.
5. Post-Processing wenn nötig

Die wahl eines guten Strafparameters rho ist entscheidend für die Konvergenz. Die simpelste Form des Kommandos lautet
`runph --model-directory=models --instance-directory=scenarios --default-rho=1`
oder kürzer
`runph -m models -i scenarios -r 1`
Wichtig sind die weiteren Zusatzbefehle, hier eine kleine Auswahl (alle Befehloptionen können mittels `runph --help` aufgerufen werden):

- `--verbose` Erzeugt deutlich mehr Output und Kommentare zum Algorithmus
- `--max-iterations=..` Ganzzahl, gibt die maximale Anzahl Iterationen an, default ist 100. 
- `--termdiff-threshold=..` Konvergenzbedingung, default ist 0.0001. Ist die Grenze für die erwartete Abweichung vom Mittelwert. 
- `--enable-normalized-termdiff-convergence` nutze die normalisierte termdiff-Bedingung.
- `--linearize-nonbinary-penalty-terms` Linearisiere quadratischen Strafterm mit stückweiser linearer Funktion, **!wichtig wenn wir als Solver glpk nutzen!** .
- `--solution-writer=pyomo.pysp.plugins.jsonsolutionwriter` schreibt die Lösungsvariable in eine JSON-Datei.
Hiermit lässt sich das Problem approximativ und zufriedenstellend lösen.

## Variablenabhängige Penalty Werte

Ein einzelner Wert für rho in der Zielfunktion des Algorithmus kann schlecht für die Konvergenz sein, weil er entweder unwichtig wird oder die eigentliche
Zielfunktion verdrängt.  Dies führt entweder zur realistischen Nichtkonvergenz oder Oszillation.

In einer Konfigurationsdatei, z.B. RHO_CFGFILE.py können wir eine Strategie zur Bestimmung des Wertes ablegen und mit `--rho-cfgfile=RHO_CFGFILE`
beim Ausführen von runph einsetzen. Diese datei kann folgendermaßen aussehen:

```
    def ph_rhosetter_callback(ph, scenario_tree, scenario):

        MyRhoFactor = 1.0
        root_node = scenario_tree.findRootNode()
        si = scenario._instance
        sm = si._ScenarioTreeSymbolMap
    for i in si.ProductSizes:
        ph.setRhoOneScenario(
            root_node,
            scenario,
            sm.getSymbol(si.NumProducedFirstStage[i]),
            si.UnitProductionCosts[i] * MyRhoFactor * 0.001)
    for j in si.ProductSizes:
        if j <= i:
            ph.setRhoOneScenario(
                root_node,
                scenario,
                sm.getSymbol(si.NumUnitsCutFirstStage[i,j]),
                si.UnitReductionCost * MyRhoFactor * 0.001)
```
Hier wird rho kostenproportional bestimmt, es wird berechnet als Funktion des Kostenkoeffizienten der Zielfunktion.
## Bundling

In Bündelmethoden werden bisher berechnete Subgradienten der aktuellen Iteration hinzugefügt, was häufig eine deutlich bessere Konvergenz bedeutet. Kombiniere
mehrere Szenarien und löse die resultierende erweiterte Form als Subproblem (Superszenario).
Das Bündeln muss in der *ScenarioStructure.dat* Datei folgendermaßen klarifiziert sein.
```
param Bundling := True ;
set Bundles := EvenBundle OddBundle ;
set BundleScenarios[OddBundle] := Scenario1 Scenario3 Scenario5 Scenario7 Scenario9 ;
set BundleScenarios[EvenBundle] := Scenario2 Scenario4 Scenario6 Scenario8 Scenario10 ;
```
Die Namen der Bündel/Szenarien sind dem Nutzer überlassen. Alternativ können wir `runph` die Bündel zufällig wählen lassen mithilfe von
- `--create-random-bundles=X` konstruiert X viele Zufallsbündel
- `--scenario-tree-seed=XXXX` legt die Zufallszahl für die Generierung der Zufallsbündel fest zur Reproduktion des Zufalls.

## Watson und Woodruff Extensions
Trotz guter Werte für rho kann Progresesive Hedging nur langsam konvergieren. Die Merkmale von dieser Erweiterung sind:
1. Erkennung der Konvergenz
2. Zykelerkennung
3. Konvergenzbasierte Optimalitätsschwellenwerte für Subprobleme
Die erweiterung muss weitesgehend vom nutzer spezifiziert werden, grundlegende Kommandos lauten:
- `--enable-ww-extensions` Erlaubt das extensions plugin
- `--ww-extension-cfgfile=WW_EXTENSION_CFGFILE` Name für die Konfigurationsdatei für das Plugin, z.B. *wwph.cfg* 
- `--ww-extension-suffixfile=WW_EXTENSION_SUFFIXFILE` Name für Suffix Datei der Variablen des WW Progressive Hedging extensions plugin, z.B. `wwph.suffixes`. Suffixe sind dafür da das Modell mit Zusatzinformation auszustatten, z.B. um extra Information über die Lösung des MOdells zu speichern.

### Kontrolle der Subprobleme und Zykeldetektion
In der *wwph.cfg* Konfigurationsdatei können wir Werte festesetzen für bestimmte Berechnungseigenschaften.
- *Iteration0MipGap* : Spezifiziert die MIP-Lücke für alle Szenario Subprobleme in Iteration 0. Standardwert ist 0.
- *InitialMipGap* : Standardwert ist 0.1
- *FinalMipGap* : Standardwert ist 0.001
- *hash_hit_len_to_slam* : Ignoriere mögliche Zyklen für Variablen, wo der Zyklus kürzer ist als dieser Wert. Standardwert ist die Anzahl der Szenarien. 10-20 bei vielen Szenarien ist häufig ein besserer Wert
- *DisableCycleDetection* : Binärer Parameter. Standarwert ist 0.


## Parallele Abarbeitung der Szenario Subprobleme 

