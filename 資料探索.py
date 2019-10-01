# %%
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

with sqlite3.connect(r'D:\\研究\\選舉研究\\資料\\data.db') as con:
    df = pd.read_sql('SELECT * FROM 推文帳號互動概況', con=con)

df.drop([0, 1, 2], inplace=True)
df.reset_index(drop=True, inplace=True)
# %%
# 取出總留言數高於10的樣本，因為低於10的帳號的互動太少，會使互動率呈現極端的數值
data = df[df['總留言數']>=10]
data.reset_index(drop=True, inplace=True)

#%%
appearance1 = data[['推文作者','總推文數','總噓文數','總留言數']].drop_duplicates()
appearance1.reset_index(drop=True, inplace=True)
appearance1['推文率']=appearance1['總推文數']/appearance1['總留言數']
appearance1['噓文率']=appearance1['總噓文數']/appearance1['總留言數']

#%%
upvote_rate = appearance1['推文率']
dnvote_rate = appearance1['噓文率']
plt.scatter(upvote_rate, dnvote_rate, s=0.5)
plt.show()

# %%
