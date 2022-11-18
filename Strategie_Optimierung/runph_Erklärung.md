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

### Variablenfixierung
Häufig ist das Fixieren von Variablen eine effiziente Heuristik um die Konvergenz zu beschleuinigen. Das Fixieren ergibt nur dann Sinn wenn eine Korrelation existiert zwischen dem konvergierten Wert einer Variable in allen Subproblemen und der ermittelten Optimallösung ohne Fixieren.

- `Iter0FixIfConvergedAtLB` Binärer Parameter, Diskrete Variablen die in allen Szenarien in der ersten Iteration ihre  untere Schranke annehmen werden fixiert.
- `Iter0FixIfConvergedAtUB` Binärer Parameter, Diskrete Variablen die in allen Szenarien in der ersten Iteration ihre  obere Schranke annehmen werden fixiert.
- `Iter0FixIfConvergedAtNB` Binärer Parameter, Diskrete Variablen die in allen Szenarien in der ersten Iteration einen gleichen Wert annehmen werden fixiert.
- `FixWhenItersConvergedAtLB` Zahl der Iterationen über diskrete Variablen, bevor diese wenn fixiert werden, wenn sie diese Zeit die untere Schranke annehmen.
- `FixWhenItersConvergedAtUB` Zahl der Iterationen über diskrete Variablen, bevor diese wenn fixiert werden, wenn sie diese Zeit die ober Schranke annehmen.
- `FixWhenItersConvergedAtNB` Zahl der Iterationen über diskrete Variablen, bevor diese wenn fixiert werden, wenn sie diese Zeit einen gleichen Wert annehmen.
- `FixWhenItersConvergedCOntinous`Analog zum letzten Fall nur für stetige Variablen (Standarwert ist 0, alles andere halte ich auch in dieser Anwendung für sinnlos bzw. zu startk vereinfacht.)

Für gemischt ganzzahlige Probleme benötig runph eventuell sehr lange um kleine Werte zu finetunen. Deswegen *slammen* wir Variablen früh, gehen
damit suboptimale Lösungen ein, aber können Zykel vermeiden und die Geschwindigkeit verbessern.

- `SlamAFterITer` Zahl der PH Iteration, ab welche Variablen geslammt werden, jeweils eine pro Iteration um Konvergenz zu erzwingen. Defaulwert: Anzahl der Szenarien.
- `CanSlamToLB` Binärer Parameter, legt fest ob diskrete Variablen zu ihrer unteren Schranke  geslammt werden können. Default ist False.
- `CanSlamToUB` Analog.
- `CanSlamToAnywhere` Analog, wird zu dem Durchschnittswert über alle Szenarien geslammt.
- `CanSlamToMin` Analog, Minimum über alle Szenarien slammen
- `CanSlamToMax` Analog.
- `PH_Iters_Between_Cycle_Slams` Kontrolliert die Anzahl der Iterationen zwischen Slams um Zykel zu zerstören. Defaultwert ist 1, also ein Slam pro Iteration, ein Wert von NUll indiziert das unbegrenzt viele Variablen pro Iteration geslammt werden können.

Wichtig ist dabei auf die Zulässigkeit zu achten. Wenn man die Variable des eingespeisten Stroms auf sein Minimum fixiert ist, z.B. Null zu einem bestimmtem Zeitpunkt, bleibt das Problem zulässig weil eine größere Menge maximal die restlichen Restrikition verletzen kann. In dem Problem kann fast alles
bis auf den gekauften Strom beliebig geslammt werden, da dieser alle anderen Restriktionen erfüllbar machen kann.

### Beschränkte erweiterte Form
Heuristik: Mache für progressive hedging ein paar Ierationen, fixiere/slamme ein paar konvergierte Variable und löse nun die geschrumpfte erweiterte Form.
Durch `--write-ef`, `--solve-ef` und `--ef-output-file=efout.lp` wird nach Terminierung von PH die erweiterte Form gelöst, inklusive vorverarbeiteten fixierten Werten aus den Subproblemen. Mit `--solver=..` muss immernoch ein Solver angegeben werden.

## Alternative Konvergenzkriterien
Von den folgenden Kriterien bzw. Konvergenzmetriken können mehrere aktiviert werden: 
- `--enable-termdiff-convergence` Terminiere PH basierend auf der unsaklierten Summer der Differenzen zwischen Variablenwerte und Mittelwert.
- `--enable-normalized-termdiff-convergence` Analog, nur wird jeder Summenterm normalisiert durch den mittleren Variablenwert.
- `--enable-free-discrete-count-convergence` Terminiere PH basierend auf der Anzahl freier diskreter Variablen. Standardwert ist False
- `--free-discrete-count-threshold=..` s.o., Grenzwert für Terminierung bei dieser Metrik.

## Nutzerdefinierte Erweiterungen 
An bestimmten Stellen des PH Workflows können wir durch Überschreibung bestimmter Funktionen in den inneren Kreislauf eingreifen. Diese werden in der read-only Datei *phextension.py* deklariert:
```
class IPHExtension(Interface):
    def post_ph_initialization(self, ph):
        """ Called after PH initialization."""
        pass
    def post_iteration_0_solves(self, ph):
        """ Called after the iteration 0 solves."""
        pass
    def post_iteration_0(self, ph):
        """ Called after the iteration 0 solves, averages
        computation, and weight update."""
        pass
    def post_iteration_k_solves(self, ph):
        """ Called after the iteration k solves."""
        pass
    def post_iteration_k(self, ph):
        """ Called after the iteration k solves, averages
        computation, and weight update."""
        pass
    def post_ph_execution(self, ph):
        """ Called after PH has terminated."""
        pass
```
## Parallele Abarbeitung der Szenario Subprobleme 

Mit Pyro (Python Remote Objects) lässt sich die Kommunikation zwischen verschieden Servern zur Lösung der Subprobleme koordinieren. Der Standard solver manager arbeitert seriell und lokal. Mit `--solver-manager=pyro` wird anstelle dessen ein Solver Manager gestartet, um die Probleme remotely abzuarbeiten. Dieser identifiziert verfügbare Solver Daemons, und koordiniert das Lösen und Abrufen dieser.

## Schranken

Es lassen sich Schranken für den Zeilfunktionswert anhand der aktuelen PH Iteration bestimmen, dazu wird `--user-defined-extension=pyomo.pysp.plugins.phboundextension` aufgerufen beim LÖsen. Dies benötigt zusätzlichen Rechenaufwand und deshalb nicht in jeder Iteration nötig.  
Mithilfe von äußeren Schranken (je nach Min/Max untere/obere Schranke) kann man zusätzliche Abbruchbedingungen für en Algorithmus definieren, z.B. `--enable-outer-bound-convergence`, `--outer-bound-convergence-threshold=VAL`
