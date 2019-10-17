# %%
import sqlite3
import pandas as pd
import igraph as ig
import cairo
import time


with sqlite3.connect(r'E:\\research\\資料\\data.db') as con:
    df = pd.read_sql(
        'SELECT 作者,文章IP,發文時間,推文類型,推文作者,推文IP,推文時間 FROM 合併資料表', con=con)

#
count_comment = df.groupby(['推文作者'], as_index=False)[
    '推文IP'].agg({'總留言數': 'count'})
count_comment_10 = count_comment[count_comment['總留言數'] > 10]
#count_comment_10.reset_index(drop=True, inplace=True)

df_comment_10 = pd.merge(count_comment_10, df, how='left', on='推文作者')


def droplose(DataFrame):
    cols = DataFrame.columns.values.tolist()
    for i in cols:
        DataFrame.drop(DataFrame.index[DataFrame[i] == ''], inplace=True)
    DataFrame.reset_index(drop=True, inplace=True)


droplose(df_comment_10)

#
df_network_ip = df_comment_10[['推文作者', '推文IP', '作者', '文章IP']]

df_network_ip_cut = df_network_ip[['作者', '文章IP']]

del df_network_ip['作者']
del df_network_ip['文章IP']

df_network_ip.columns = ['帳號', 'IP']
df_network_ip_cut.columns = ['帳號', 'IP']

df_network_ip = pd.concat([df_network_ip, df_network_ip_cut])
df_network_ip.drop_duplicates(inplace=True)
df_network_ip.reset_index(drop=True, inplace=True)

#
name_list = df_network_ip[['帳號']].drop_duplicates()
name_list.reset_index(drop=True, inplace=True)
name_list.reset_index(inplace=True)  # 用來加入序號作為ID
name_list.columns = ['ID', '帳號']

df_network_ip = pd.merge(name_list, df_network_ip, how='left', on='帳號')

column_edge = 'IP'
column_ID = 'ID'

data_to_merge = df_network_ip[[column_ID, column_edge]]
data_to_merge = data_to_merge.merge(data_to_merge[[column_ID, column_edge]].rename(
    columns={column_ID: column_ID+'_2'}), on=column_edge)

d = data_to_merge[~(data_to_merge[column_ID] == data_to_merge[column_ID+"_2"])] \
    .dropna()[[column_ID, column_ID+"_2", column_edge]]

d.drop(d.loc[d[column_ID+"_2"] < d[column_ID]].index.tolist(), inplace=True)
d.reset_index(drop=True, inplace=True)
#
edge_list = []
for i in range(d.shape[0]):
    edge = (d.iloc[i, 0], d.iloc[i, 1])
    edge_list.append(edge)

#
'''
edge_df = pd.DataFrame(edge_list)
edge_df.columns = ['ID1', 'ID2']

edge_grouped_id1 = edge_df.groupby(['ID1'], as_index=False)['ID2'].agg({'cnt': 'count'})
edge_count_1 = edge_grouped_id1['cnt']>1
'''
#%%
g = ig.Graph()

g.add_vertices(len(name_list['ID']))
g.vs['name'] = name_list['帳號']
g.add_edges(edge_list)
g.es['IP'] = d['IP']


def getDegree_lower(graph, lower_then):
    degree = graph.degree()
    index = []
    for i in range(len(degree)):
        if degree[i] < lower_then:
            index.append(i)

    return index


g.delete_vertices(getDegree_lower(g, 50))

# %%
time_s = time.time()

layout = g.layout("kk")

visual_style = {}
visual_style["vertex_size"] = 5
visual_style["vertex_label"] = g.vs["name"]
visual_style["vertex_label_size"] = 6
visual_style["layout"] = layout

print(ig.plot(g, **visual_style))

time_e = time.time()
time_cost = time_e - time_s
print(time_cost)
# %%
