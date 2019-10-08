# %%
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import time

database = r'E:\\research\\資料\\data.db'
#database = r'D:\\研究\\選舉研究\\資料\\data.db'

# %%
with sqlite3.connect(database) as con:
    df_push = pd.read_sql('SELECT * FROM 推文帳號互動概況', con=con)

df_push.drop([0, 1, 2], inplace=True)
df_push.reset_index(drop=True, inplace=True)
# %%
# 取出總留言數高於10的樣本，因為低於10的帳號的互動太少，會使互動率呈現極端的數值
data_push = df_push[df_push['總留言數'] >= 10]
data_push.reset_index(drop=True, inplace=True)

# %%
appearance1 = data_push[['推文作者', '總推文數', '總噓文數', '總留言數']].drop_duplicates()
appearance1.reset_index(drop=True, inplace=True)
appearance1['推文率'] = appearance1['總推文數']/appearance1['總留言數']
appearance1['噓文率'] = appearance1['總噓文數']/appearance1['總留言數']

with sqlite3.connect(r'D:\\研究\\選舉研究\\資料\\data_push.db') as con:
    appearance1.to_sql(name='PTT用戶面貌', con=con,
                       if_exists='append', index=False)


# %%
path = r'D:\\研究\\選舉研究\\資料\\死忠程度\\'
rank = [0.5, 0.6, 0.7, 0.8, 0.9]
rankname = ['50', '60', '70', '80', '90']
for i in range(len(rank)):
    result = data_push[data_push['在此作者下的留言機率'] >= rank[i]]
    result.to_csv(path + '死忠程度' +
                  rankname[i] + '.csv', encoding='cp950', index=0)

# %%
with sqlite3.connect(database) as con:
    df_network_ip = pd.read_sql("SELECT 推文作者,推文IP,作者,文章IP FROM 合併資料表", con=con)

def droplose(DataFrame):
    cols = DataFrame.columns.values.tolist()
    for i in cols:
        DataFrame.drop(DataFrame.index[DataFrame[i] == ''], inplace=True)
    DataFrame.reset_index(drop=True, inplace=True)
    

# %%
# 整理資料
droplose(df_network_ip)

df_network_ip_cut = df_network_ip[['作者', '文章IP']]

del df_network_ip['作者']
del df_network_ip['文章IP']

df_network_ip.columns = ['帳號', 'IP']
df_network_ip_cut.columns = ['帳號', 'IP']

df_network_ip = pd.concat([df_network_ip, df_network_ip_cut])
df_network_ip.drop_duplicates(inplace=True)
df_network_ip.reset_index(drop=True, inplace=True)

# %%

column_edge = 'IP'
column_ID = '帳號'

data_to_merge = df_network_ip[[column_ID, column_edge]]
data_to_merge = data_to_merge.merge(data_to_merge[[column_ID, column_edge]].rename(columns={column_ID:column_ID+'_2'}),on=column_edge)

#%%
d = data_to_merge[~(data_to_merge[column_ID] == data_to_merge[column_ID+"_2"])] \
    .dropna()[[column_ID, column_ID+"_2", column_edge]]

d.drop(d.loc[d[column_ID+"_2"] < d[column_ID]].index.tolist(), inplace=True)

#d.to_csv('edge.csv')
#%%
test = d[:100]
account = df_network_ip['帳號'].drop_duplicates()

start_time = time.time()

G = nx.from_pandas_edgelist(df=test, source=column_ID, target=column_ID+'_2', edge_attr=column_edge)

G.add_nodes_from(nodes_for_adding=account.tolist())

print(nx.draw(G))

end_time = time.time()

print("It cost %f sec" % (end_time - start_time))
#%%
