# Optimierung Elektromanagement
Stochastische Optimierung des Elektromanagements eines Wohnhauses

# Deterministischer Fall
Um die Optimierung mit dem abstrakten Modell durchzuführen muss zunächst
test_write_data.py ausgeführt werden und der Zeitraum eingestellt werden.
Anschließend wird das ReferenceModel.py für die Optimierung ausgeführt.

# Stochastischer Fall
Das zusätzliche Beziehen von Strom aus dem Netz wird als Recourse Aktion gesehen:
Falls nach Realisierung des Zufalls zu einem Zeitpunkt zu wenig Strom vorhanden 
ist um die Restriktionen zu erfüllen, muss dies ausgeglichen werden.

## Workflow stochastische Optimierung
1. Szenariodaten generieren durch Aufrufen von scenario_generation.py, Einstellen von Datum und Szenarien
2. Im Ordner .\Stochastische_Optimierung_Wohnhaus  wird durch Aufrufen des Befehls
<p>runef -m models -s scenarios --solve --solver=glpk --solution-writer=pyomo.pysp.plugins.jsonsolutionwriter</p>
das stochastische Optimierungsproblem in erweiterter Formulierung mit glpk gelöst, mit Referenzmodell im Ordner models und
Szenariodateien im Ordner scenarios.
3. Rufe Result_pickler.py auf um die Lösungen aus der .json Datei seriell und seperat abzuspeichern.
4. Stelle in visualize_solution das gewünschte Datum ein, Lastprofil wird generiert. 
