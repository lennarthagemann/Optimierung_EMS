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
