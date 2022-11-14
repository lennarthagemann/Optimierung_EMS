import re
from math import sin

def lex_to_num_sorter(dict):
    """
    Sortiere ein Dictionary mit keys der Form (Variablenname)[t(number)]. 
    """
    print(sorted(dict , key=lambda x: re.findall('\d+', x)[0]))
    return {t : dict[t] for t in sorted(dict , key=lambda x: int(x.split('[t')[1].split(']')[0]))}


l = {'z[t0]'  : 2, 'z[t1]'  : 2, 'z[t10]'  : 2, 'z[t11]'  : 2, 'z[t12]'  : 2, 'z[t13]'  : 2, 'z[t14]'  : 2, 'z[t15]'  : 2, 'z[t16]'  : 2, 
'z[t17]'  : 2, 'z[t18]'  : 2, 'z[t19]'  : 2, 'z[t2]'  : 2, 'z[t3]'  : 2, 'z[t4]'  : 2, 'z[t5]'  : 2, 'z[t6]'  : 2, 'z[t7]'  : 2, 'z[t8]'  : 2, 'z[t9]'  : 2, }
print(l)
print(lex_to_num_sorter(l))