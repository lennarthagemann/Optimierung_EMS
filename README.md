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

Im Ordner .\Stochastische_Optimierung_Wohnhaus wird durch Aufrufen des Befehls
 runef -m models -s scenarios --solve --solver=glpk
das stochastische Optimierungsproblem in erweiterter Formulierung mit glpk gelöst, mit Referenzmodell im Ordner models und
Szenariodateien im Ordner scenarios.
