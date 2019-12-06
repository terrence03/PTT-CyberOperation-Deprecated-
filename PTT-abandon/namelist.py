# %%
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime


# %%
def clean_namelist(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        result = file.read()

    result = result.replace('\n', ',').replace('、', ',').replace('.', ',')
    namelist = result.split(',')

    for i in range(len(namelist)):
        namelist[i] = namelist[i].strip()

    namelist = ' '.join(namelist).replace('  ', ' ')
    namelist = namelist.split(' ')

    namelist1 = []
    for j in range(len(namelist)):
        if namelist[j] != '':
            namelist1.append(namelist[j])
    
    return namelist1


# %%
with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
    df = pd.read_sql(
        'SELECT Author,postID, time, Weekday, Hour FROM onlinetime', con)


# %%
