# %%
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

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

with sqlite3.connect(r'D:\\研究\\選舉研究\\資料\\data.db') as con:
    appearance1.to_sql(name='PTT用戶面貌', con=con, if_exists='append', index=False)


#%%
path = r'D:\\研究\\選舉研究\\資料\\死忠程度\\'
rank = [0.5, 0.6, 0.7, 0.8, 0.9]
rankname = ['50', '60', '70', '80', '90']
for i in range(len(rank)):
    result = data[data['在此作者下的留言機率'] >= rank[i]]
    result.to_csv(path + '死忠程度' + rankname[i] + '.csv', encoding='cp950', index=0)

#%%
