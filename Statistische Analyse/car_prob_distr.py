"""
---------------------

Erstelle eine Wahrscheinlichkeitsverteilung für die Ladesessions eines Autos.

-Geometrische Verteilung für das Ankommen eines neuen E-Autos: Je länger die letzte Ladesession her ist,
desto wahrscheinlichlciher wird es, das wieder geladen wird (Aber die Person kann anderswo geladen haben,
weswegen dies keine echte Wahrscheinlichkeitsverteilung seien soll, aber mindestens monoton steigend.)
-Wahrscheinlichkeiten für einen bestimmten Startzeitpunkt je nach Tag, z.B. früh morgens oder am Feierabend wahrscheinlicher
-Wahrscheinlichkeit der Dauer je nach approximativer Ladegeschwindigkeit
-


---------------------
"""

class car_distr(stats.rv_continuous):
    def _cdf(self, x):
        return
    def _stats(self):
        return