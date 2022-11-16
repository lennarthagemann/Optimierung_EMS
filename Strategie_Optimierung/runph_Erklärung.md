# runph

Diese Lösungsstrategie basiert auf dem **Progressiven Hedging** zur Dekomposition.
Da das Problem möglicherweise viele Szenarien hat und eine  große Anzahl binärer Variablen in der 
ersten Stufe, ist es einerseits zwar effizient lösbar mit Schnittebenenstrategien. Das
`runef` Kommando ist jedoch nicht mehr ausreichend, da die erweiterte Form zu groß wird.
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


## Bundling

In Bündelmethoden werden bisher berechnete Subgradienten der aktuellen Iteration hinzugefügt, was häufig eine deutlich bessere Konvergenz bedeutet. Kombiniere
mehrere Szenarien und löse die resultierende erweiterte Form als Subproblem (Superszenario).
Das Bündeln muss in der *ScenarioStructure.dat* Datei folgendermaßen klarifiziert sein.
```
{
    param Bundling := True ;
    set Bundles := EvenBundle OddBundle ;
    set BundleScenarios[OddBundle] := Scenario1 Scenario3 Scenario5 Scenario7 Scenario9 ;
    set BundleScenarios[EvenBundle] := Scenario2 Scenario4 Scenario6 Scenario8 Scenario10 ;
}
```
Die Namen der Bündel/Szenarien sind dem Nutzer überlassen. Alternativ können wir `runph` die Bündel zufällig wählen lassen mithilfe von
- `--create-random-bundles=X` konstruiert X viele Zufallsbündel
- `--scenario-tree-seed=` legt die Zufallszahl für die Generierung der Zufallsbündel fest zur Reproduktion des Zufalls.

