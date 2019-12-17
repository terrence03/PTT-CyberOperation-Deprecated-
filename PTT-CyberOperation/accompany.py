# %%
import community
import matplotlib.pyplot as plt
import networkx as nx
from scipy import stats
import sqlite3
import pandas as pd
import numpy as np


# %%
db_path = r'D:\\research\\data\\sql\\analysis.db'
with sqlite3.connect(db_path) as con:
    post = pd.read_sql(
        'SELECT post_ID, post_Author, post_IP FROM original_post', con)
    push = pd.read_sql(
        'SELECT post_ID, com_User, com_IP FROM original_push', con)
    df = pd.merge(post, push, 'left', 'post_ID')

# %%
# 文章作者與留言者的忠誠度
data = df[['post_ID', 'post_Author', 'com_User']]
data.drop(data.loc[(data['post_Author'] == data['com_User'])
                   ].index.tolist(), inplace=True)  # 刪除自回留言


# %%

data.drop(data[data['com_User'] == ''].index.tolist(), inplace=True)
data.dropna(inplace=True)
data['count'] = 1

data = data.groupby(['post_ID', 'post_Author', 'com_User'],
                    as_index=False)[['count']].count()
data['count_1'] = 1

data = data.groupby(['com_User', 'post_Author'], as_index=False)[
    ['count_1']].sum()
sum_user = data.groupby('com_User', as_index=False)[['count_1']].sum()

data = pd.merge(data, sum_user, 'left', 'com_User')
data.columns = ['com_User', 'post_Author', 'count_com_1', 'sum_com_1']
data['com_%'] = data['count_com_1']/data['sum_com_1']


# %%


def get_datainfo(DataFrame, fliter=[0, 0, 0]):
    count_fliter = fliter[0]
    sum_fliter = fliter[1]
    percentage_fliter = fliter[2]

    DataFrame_fliter = (DataFrame['count_com_1'] >= count_fliter) & (
        DataFrame['sum_com_1'] >= sum_fliter) & (DataFrame['com_%'] >= percentage_fliter)
    DataFrame = DataFrame.loc[DataFrame_fliter]

    grouped_1 = DataFrame.groupby(['com_User'], as_index=False)[
        'count_com_1'].mean()
    grouped_2 = DataFrame.groupby(['com_User'], as_index=False)[
        'sum_com_1'].mean()

    print('總共: ' + str(len(set(DataFrame['com_User']))) + ' 個留言帳號')
    print('count_com_1 平均值: ' + str(np.mean(grouped_1['count_com_1'])))
    print('count_com_1 最大值: ' + str(np.max(DataFrame['count_com_1'])))
    print('count_com_1 最小值: ' + str(np.min(DataFrame['count_com_1'])))
    print('count_com_1 中位數: ' + str(np.median(grouped_1['count_com_1'])))
    print('count_com_1   眾數: ' +
          str(stats.mode(grouped_1['count_com_1'])[0][0]))
    print('count_com_1 標準差: ' + str(np.std(grouped_1['count_com_1'])))
    print('sum_com_1   平均值: ' + str(np.mean(grouped_2['sum_com_1'])))
    print('sum_com_1   最大值: ' + str(np.max(DataFrame['sum_com_1'])))
    print('sum_com_1   最小值: ' + str(np.min(DataFrame['sum_com_1'])))
    print('sum_com_1   中位數: ' + str(np.median(grouped_2['sum_com_1'])))
    print('sum_com_1     眾數: ' + str(stats.mode(grouped_2['sum_com_1'])[0][0]))
    print('sum_com_1   標準差: ' + str(np.std(grouped_2['sum_com_1'])))
    print('com_%       平均值: ' + str(np.mean(DataFrame['com_%'])))
    print('com_%       最大值: ' + str(np.max(DataFrame['com_%'])))
    print('com_%       最小值: ' + str(np.min(DataFrame['com_%'])))
    print('com_%       中位數: ' + str(np.median(DataFrame['com_%'])))
    print('com_%         眾數: ' + str(stats.mode(DataFrame['com_%'])[0][0]))
    print('com_%       標準差: ' + str(np.std(DataFrame['com_%'])))


def test_in_calist(namelist):
    ca = pd.read_excel(r'E:\\research\\data\\候選人資料\\ca.xlsx')
    mask = (ca['com_User'].isin(namelist))
    return ca.loc[mask]


def get_fliterdata(DataFrame, count_over=0, sum_over=0, percentage_over=0.3):
    mask = (DataFrame['count_com_1'] >= count_over) & (DataFrame['sum_com_1'] >= sum_over) & (
        DataFrame['com_%'] >= percentage_over)
    df_totest = DataFrame.loc[mask]
    return df_totest


def get_nodelist(DataFrame, count_over=0, sum_over=0, percentage_over=0.3):
    mask = (DataFrame['count_com_1'] >= count_over) & (DataFrame['sum_com_1'] >= sum_over) & (
        DataFrame['com_%'] >= percentage_over)
    df_totest = DataFrame.loc[mask]
    User_list = list(set(df_totest['com_User']))
    Author_list = list(set(df_totest['post_Author']))
    node_list = list(set(User_list+Author_list))

    return node_list


def get_edgelist(DataFrame, count_over=0, sum_over=0, percentage_over=0.3):
    mask = (DataFrame['count_com_1'] >= count_over) & (DataFrame['sum_com_1'] >= sum_over) & (
        DataFrame['com_%'] >= percentage_over)
    df_totest = DataFrame.loc[mask]
    zipped = zip(df_totest['com_User'].tolist(),
                 df_totest['post_Author'].tolist())

    return list(zipped)


# %%
count_fliter = 3
# 此值會過濾掉留言者對作者留言次數過低的樣本，網軍此值理論上比一般人高
sum_fliter = 5
# 此值會過濾掉留言者總留言次數過低的樣本
percentage_fliter = 0.3
# 此值會過濾掉留言者對作者留言機率過低的樣本，網軍此值理論上比一般人高


G = nx.Graph()
G.add_nodes_from(get_nodelist(data, count_fliter,
                              sum_fliter, percentage_fliter))
G.add_edges_from(get_edgelist(data, count_fliter,
                              sum_fliter, percentage_fliter))

nx.graph_number_of_cliques(G)

partition = community.best_partition(G)
pos = nx.spring_layout(G)
plt.figure(figsize=(8, 8), dpi=300)
plt.axis('off')
nx.draw_networkx_nodes(G, pos, node_size=20,
                       cmap=plt.cm.RdYlBu, node_color=list(partition.values()), label=get_nodelist(data, count_fliter, sum_fliter, percentage_fliter))
nx.draw_networkx_edges(G, pos, alpha=0.3)

nx.write_gexf(G, r'E:\\research\\data\\圖庫\\test.gexf')
plt.show(G)


# %%
clique = pd.DataFrame(
    [pd.Series(partition).index.tolist(), pd.Series(partition).tolist()]).T
clique.columns = ['com_User', 'user_Clique']
testdata = get_fliterdata(data, count_fliter, sum_fliter, percentage_fliter)
testdata = pd.merge(testdata, clique, 'left', 'com_User')

testdata.to_excel(r'E:\\research\\data\\網軍關係.xlsx',index=False)

# %%
