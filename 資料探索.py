# %%
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

with sqlite3.connect(r'E:\\research\\資料\\data.db') as con:
    df = pd.read_sql('SELECT * FROM 推文帳號互動概況', con=con)

df.drop([0, 1, 2], inplace=True)
df.reset_index(drop=True, inplace=True)
# %%
grouped_comment = df.groupby('推文作者')[['在此作者下的留言機率']]

# %%
