import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

#print(norm.__doc__)



"""
-------------------------------
Verteilung an empirische Werte passen
-------------------------------
"""

df = pd.DataFrame({'a' : np.random.normal(loc=0, scale=2, size=10000),
                   'b' : np.arange(10000)})

print(df['a'][df['a'] <= -1].count()/df['a'].count())

"""
-------------------------------
Eigene Verteilung schreiben
-------------------------------
"""