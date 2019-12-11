# %%
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


def test_in_calist(namelist):
    ca = pd.read_excel(r'E:\\research\\data\\候選人資料\\ca.xlsx')
    mask = (ca['com_User'].isin(namelist))
    return ca.loc[mask]


def get_nodelist(DataFrame, count_over_than=0, percentage_over_than=0.3):
    mask = (DataFrame['count_com_1'] >= count_over_than) & (
        DataFrame['com_%'] >= percentage_over_than)
    df_totest = DataFrame.loc[mask]
    User_list = list(set(df_totest['com_User']))
    Author_list = list(set(df_totest['post_Author']))
    node_list = list(set(User_list+Author_list))
    
    return node_list

def get_edgelist(DataFrame, count_over_than=0, percentage_over_than=0.3):
    mask = (DataFrame['count_com_1'] >= count_over_than) & (
        DataFrame['com_%'] >= percentage_over_than)
    df_totest = DataFrame.loc[mask]
    zipped = zip(df_totest['com_User'].tolist(), df_totest['post_Author'].tolist())

    return list(zipped)

# %%
import networkx as nx
import matplotlib.pyplot as plt
G = nx.Graph()
G.add_nodes_from(get_nodelist(data,2))
G.add_edges_from(get_edgelist(data,2))
nx.draw(G)
# %%
