# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 11:25:39 2022

@author: hagem
"""

from Preprocessing_Functions import pv_generation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

date='2005-01-01'
pv_date = pv_generation(date)
print(pv_date)
plt.step(np.arange(np.shape(pv_date)[0]), pv_date)
