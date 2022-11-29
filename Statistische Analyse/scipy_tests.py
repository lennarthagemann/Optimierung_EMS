import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

#print(norm.__doc__)

a = np.arange(-2,2, 0.5)
print(a)
print(norm.cdf(a))
print(norm.mean(), norm.std(), norm.var())

#Inverse der cdf -> ppf, Dadurch finden wir den Median der Verteilung (norm.ppf(0.5) => 50% der Werte sind kleiner als der Funktionswert)

print(norm.ppf(np.arange(0,1,0.1)))

"""
-------------------------------
Verteilung an empirische Werte passen
-------------------------------
"""



"""
-------------------------------
Eigene Verteilung schreiben
-------------------------------
"""