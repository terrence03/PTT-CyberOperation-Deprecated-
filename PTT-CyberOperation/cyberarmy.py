# %%
# 導入函式庫
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from matplotlib import pyplot as plt
import seaborn as sns
import networkx as nx
import community
from tqdm import tqdm
import os

path = r'D:\\research\\data\\alldata\\'

# 導入文章與推文資料資料
with sqlite3.connect(path+'analysis.db') as con:
    df_post = pd.read_sql('SELECT * FROM original_post', con)
    df_post['post_Datetime'] = df_post['post_Datetime'].map(
        lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))    # 時間轉為datetime格式

    df_com = pd.read_sql('SELECT * FROM original_push', con)
    df_com.dropna(inplace=True)
    df_com['com_Datetime'] = df_com['com_Datetime'].map(
        lambda x: datetime.strptime(x, '%Y/%m/%d %H:%M'))    # 時間轉為datetime格式
    df_com.drop(df_com[df_com['com_User'] == ''].index.tolist(), inplace=True)

    # 導入候選人資料
df_cand_info = pd.read_excel(path+'candidate_info.xlsx')

Type = {'推': 1, '→': 0, '噓': -1}
df_com['com_Type'] = df_com['com_Type'].map(lambda x: Type[x])

# %%
#############################
#####    篩選條件設定    #####
#############################

# 條件一 活躍程度
condition1_1 = 0.5  # 前多少%的活躍用戶
condition1_2 = 2    # 用戶留言下限則數(每則留言算作1則)

# 條件二 偏好程度
condition2_1 = 'sum&max'    # 用什麼方式決定改用戶偏好某政黨

# 條件三 上線時長
condition3_1 = 59.10    # 取多少秒的反應時間作為篩選標準

# 條件四 死忠程度
condition4_1 = 2    # 此值會過濾掉留言者對作者留言次數過低的樣本，網軍此值理論上比一般人高
condition4_2 = 2    # 此值會過濾掉留言者總留言次數過低的樣本
condition4_3 = 0.2  # 此值會過濾掉留言者對作者留言機率過低的樣本，網軍此值理論上比一般人高


# %%
#############################
#####  準備文章基本資料  #####
#############################


def get_keywordslist(DataFrame, title_col):
    '''
    DataFrame: 必須是一個有包含標題欄的資料表

    title_col: 標題欄的名稱

    返回DataFrame[title_col]所包含的候選人關鍵字的列表
    返回的列表的關鍵字已經被替換為候選人姓名
    '''
    data = DataFrame[title_col]

    key_dict = {}
    for key, value in zip(df_cand_info['Keyword'], df_cand_info['Candidate']):
        key_dict[key] = value
    key = list(key_dict.keys())
    value = list(key_dict.values())

    KW = []
    for i in tqdm(range(len(data))):
        kwlist = []
        for j in range(len(key_dict)):
            if key[j] in DataFrame.loc[i, title_col]:
                kwlist.append(value[j])
            kw = ','.join(set(kwlist))
        KW.append(kw)

    return KW


def fillkeywords(DataFrame):
    '''
    DataFrame: 包含了Keywords欄的資料表

    將空的關鍵字欄填上候選人

    * 部分標題以為是內標的關係所以可能被作者修改過，找不到候選人關鍵字了
    所以使用原本候選人的名稱填入作為關鍵字
    '''
    for i in range(len(DataFrame['keywords'])):
        if DataFrame.loc[i, 'keywords'] == '':
            DataFrame.loc[i, 'keywords'] = DataFrame.loc[i, 'Candidate']


df_post['keywords'] = get_keywordslist(df_post, 'post_Title')  # 建立關鍵字欄
fillkeywords(df_post)  # 填滿空的關鍵字欄

# 特殊選項 只取談論一個候選人的文章
df_post = df_post.loc[(df_post['keywords'].str.len() <= 3)]

df_merge = pd.merge(df_post, df_com, 'left', 'post_ID')    # 將文章資料和留言資料結合
df_merge = pd.merge(
    df_cand_info[['Candidate', 'Region', 'Party']].drop_duplicates(), df_merge, 'left', 'Candidate')
df_merge.dropna(inplace=True)
df_merge.drop(df_merge[df_merge['com_User'] ==
                       ''].index.tolist(), inplace=True)


def get_candidate_summary(candidate):
    '''
    填入一個候選人

    取得該候選人的[候選人名稱, 文章作者數, 文章數, 留言者數, 留言數]
    '''
    candidate_list_in = df_post['Candidate'].drop_duplicates().tolist()
    if candidate in candidate_list_in:
        select = (df_merge['keywords'].str.contains(candidate))
        d = df_merge[select]
        c = d.groupby(['post_Author', 'post_ID', 'com_User'],
                      as_index=False)[['com_Content']].count()

        n_author = len(c['post_Author'].drop_duplicates().tolist())
        n_post = len(c['post_ID'].drop_duplicates().tolist())
        n_user = len(c['com_User'].drop_duplicates().tolist())
        n_com = c['com_Content'].sum()
    else:
        n_author = np.nan
        n_post = np.nan
        n_user = np.nan
        n_com = np.nan

    return [candidate, n_author, n_post, n_user, n_com]


def candidate_summary():
    '''
    用來產生所有候選人概況的資料表
    '''
    candidate_list = df_cand_info['Candidate'].drop_duplicates(
    ).tolist()   # 建立候選人列表
    summary = []
    for i in tqdm(range(len(candidate_list))):
        summary.append(get_candidate_summary(candidate_list[i]))

    summary = pd.DataFrame(summary, columns=['Candidate', 'post_Author',
                                             'post_ID', 'com_User', 'com_Content'])
    return pd.DataFrame(summary)


# %%
##############################
######  條件一 活躍程度  ######
##############################

def get_quantile_from_candidate(candidate, quantile, lower_limit=0):
    '''
    candidate: 填入一個候選人

    quantile: 填入一個百分位數，介於0-1之間

    lower_limit: 設定留言數下限，低於此數則不列入計算，預設為0

    返回一個候選人在某百分位數下的留言數
    '''

    candidate_list_in = df_post['Candidate'].drop_duplicates(
    ).tolist()  # 建立資料中出現過的候選人列表

    if candidate in candidate_list_in:
        select = (df_merge['keywords'].str.contains(candidate))
        d = df_merge.loc[select]
        c = d.groupby('com_User', as_index=False)[['com_Content']].count()
        g = c.loc[(c['com_Content'] >= lower_limit)]
        q = g['com_Content'].quantile(quantile)
        ca = g.loc[(g['com_Content'] >= q)]
        ca['Candidate'] = candidate

    else:
        na = {'com_User': np.nan, 'com_Content': np.nan, 'Candidate': candidate}
        ca = pd.DataFrame(na, [0])

    return ca


def get_active_data(quantile, lower_limit=0):
    '''
    quantile: 填入一個百分位數，介於0-1之間

    lower_limit: 設定留言數下限，低於此數則不列入計算，預設為0

    返回全部候選人在某百分位數下的留言資料
    '''

    candidate_list = df_cand_info['Candidate'].drop_duplicates().tolist()

    result = None
    for c in candidate_list:
        result = pd.concat(
            [result, get_quantile_from_candidate(c, quantile, lower_limit)])
    result = result[['Candidate', 'com_User', 'com_Content']]

    return result


test70 = get_active_data(condition1_1, condition1_2)    # ★第一條件篩選結果
test70.dropna(inplace=True)
'''
下面的程式碼正在調整中

data_1 = data[['keywords', 'com_Type', 'com_User']]
data_1.dropna(inplace=True)


def get_polarity(text):
    candidate = text.split(',')[0]
    user = text.split(',')[1]
    select = (data_1['com_User'] == user) & (
        data_1['keywords'].str.contains(candidate))
    d = data_1.loc[select]
    polarity = d['com_Type'].sum()

    return polarity



CyberArmy80.dropna(inplace=True)
CyberArmy80['text'] = CyberArmy80['Candidate'] + ',' + CyberArmy80['com_User']
CyberArmy80['polarity'] = CyberArmy80['text'].apply(lambda x: get_polarity(x))

del CyberArmy80['text']
'''


# %%
##############################
######  條件二 偏好程度  ######
##############################

# 實際上是在條件一的名單上，加入每個帳號在每個地區的偏好政黨，並刪掉一些沒有較明顯偏好的帳號

def prefer_party(DateFrame, Criterion, multiple=1):
    '''
    Dataframe: 填入一個包含['com_User', 'Region', 'Party', 'polarity']的資料表

    Criterion: 填入喜好的標準, 
    'sum'表示User對某政黨的偏好>=所有政黨的偏好總和; 
    'max'表示User對某政黨的偏好值=三者的最大值; 
    'sum&max'表示需要符合sum和max的條件

    multiple: 預設為1, 此值表示喜好標準的倍率
    '''

    if type(DateFrame) == set:
        df = df_merge.groupby(['com_User', 'Region', 'Party'], as_index=False)[
            'com_Type'].agg({'polarity': 'sum'})
        df = df.loc[(df['com_User'].isin(DateFrame))]
    else:
        df = DateFrame

    if Criterion == 'sum':
        data = df.groupby(['com_User', 'Region'], as_index=False)[
            'polarity'].sum()
    elif Criterion == 'max':
        data = df.groupby(['com_User', 'Region'], as_index=False)[
            'polarity'].max()
    elif Criterion == 'sum&max':
        data = df.groupby(['com_User', 'Region'], as_index=False)[
            'polarity'].agg({'sum': 'sum', 'max': 'max'})
        data['sum&max'] = np.nan
        for s in tqdm(range(len(data['com_User']))):
            data.iloc[s, 4] = max(
                [data.iloc[s, 2], data.iloc[s, 3]])
        del data['sum']
        del data['max']

    data = pd.merge(df, data, 'left',
                    ['com_User', 'Region'])
    data['perfer_party'] = np.nan
    data['perfer_value'] = np.nan

    for i in tqdm(range(len(data['com_User']))):
        if data.iloc[i, 3] >= data.iloc[i, 4]*multiple and data.iloc[i, 3] > 0:    # 特殊條件
            data.iloc[i, 5] = data.iloc[i, 2]
            data.iloc[i, 6] = data.iloc[i, 3] - \
                data.iloc[i, 4]

        else:
            data.iloc[i, 5] = np.nan

    if Criterion == 'sum':
        data.columns = ['com_User', 'Region', 'Party',
                        'polarity', 'polarity_sum', 'prefer_party', 'prefer_value']
    elif Criterion == 'max':
        data.columns = ['com_User', 'Region', 'Party',
                        'polarity', 'polarity_max', 'prefer_party', 'prefer_value']
    elif Criterion == 'max':
        data.columns = ['com_User', 'Region', 'Party',
                        'polarity', 'polarity_sum&max', 'prefer_party', 'prefer_value']

    print('共有: ' + str(len(set(data.dropna()['com_User']))) + ' 個用戶')

    return data.dropna()


polarity = df_merge.groupby(['com_User', 'Region', 'Party'], as_index=False)[
    'com_Type'].agg({'polarity': 'sum'})

test70 = pd.merge(test70, df_cand_info[[
                  'Candidate', 'Region', 'Party']].drop_duplicates(), 'left', 'Candidate')

test70 = pd.merge(test70, polarity, 'left', on=['com_User', 'Region', 'Party'])
test70_p = test70[['com_User', 'Region', 'Party', 'polarity']]

test_ca = prefer_party(test70_p, condition2_1)  # ★第二條件篩選結果(已包含條件一)


# %%
##############################
######  條件三 上線時長  ######
##############################


def get_response_timedelta(DataFrame):
    response_time = DataFrame.groupby(
        ['com_User', 'post_ID', 'post_Datetime'], as_index=False)['com_Datetime'].min()
    response_time['time_difference'] = (
        response_time['com_Datetime'] - response_time['post_Datetime'])
    response_time['time_difference'] = response_time['time_difference'].map(
        lambda x: x.seconds/60)

    return response_time


def response_time_info(DataFrame):
    '''
    DataFrame: 含有[time_diffience]的資料表

    返回所有帳號反應時間的基本資訊

    *帳號反應時間是某帳號對所有文章的反應時間的中位數
        '''

    data = DataFrame.groupby(['com_User'], as_index=False)[
        ['time_difference']].median()['time_difference']
    mean = np.mean(data)
    median = np.median(data)
    Max = np.max(data)
    Min = np.min(data)
    std = np.std(data)

    print('單位  :       秒')
    print('平均值: %8.2f' % mean)
    print('中位數: %8.2f' % median)
    print('最大值: %8.2f' % Max)
    print('最小值: %8.2f' % Min)
    print('標準差: %8.2f' % std)


df_timedelta = get_response_timedelta(df_merge)
df_timedelta = df_timedelta.groupby(['com_User'], as_index=False)[
    ['time_difference']].median()

response_criterion = condition3_1
time_mask = (df_timedelta['time_difference'] <= response_criterion)

time_calist = df_timedelta.loc[time_mask]   # ★第三條件篩選結果


# %%
##############################
######  條件四 死忠程度  ######
##############################
# 文章作者與留言者的忠誠度


df_acc = df_merge[['post_ID', 'post_Author', 'com_User']]
df_acc.drop(df_acc.loc[(df_acc['post_Author'] == df_acc['com_User'])
                       ].index.tolist(), inplace=True)  # 刪除自回留言

# 計算回應機率，在同一篇文章中多次回應只會被計為1
df_acc['count'] = 1
df_acc = df_acc.groupby(['post_ID', 'post_Author', 'com_User'],
                        as_index=False)[['count']].count()
df_acc['count_1'] = 1

df_acc = df_acc.groupby(['com_User', 'post_Author'], as_index=False)[
    ['count_1']].sum()
sum_user = df_acc.groupby('com_User', as_index=False)[['count_1']].sum()

df_acc = pd.merge(df_acc, df_acc.groupby('com_User', as_index=False)[
                  ['count_1']].sum(), 'left', 'com_User')
df_acc.columns = ['com_User', 'post_Author', 'count_com_1', 'sum_com_1']
df_acc['com_%'] = df_acc['count_com_1']/df_acc['sum_com_1']


def get_datainfo(DataFrame, fliter=[0, 0, 0]):
    '''
    DataFrame: 請使用上面程式獲得的df_acc資料

    fliter: 預設為[0, 0, 0]; 
    第一位數: 某帳號對另一帳號的留言次數; 
    第二位數: 某帳號全部的留言次數; 
    地三位數: 某帳號對另一帳號的留言機率

    返回的資料會過濾掉低於fliter的樣本
    '''
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
# 建議先使用get_datainfo()來決定過濾標準


count_fliter = condition4_1
# 此值會過濾掉留言者對作者留言次數過低的樣本，網軍此值理論上比一般人高
sum_fliter = condition4_2
# 此值會過濾掉留言者總留言次數過低的樣本
percentage_fliter = condition4_3
# 此值會過濾掉留言者對作者留言機率過低的樣本，網軍此值理論上比一般人高

# 繪製社群網路圖
G = nx.Graph()
G.add_nodes_from(get_nodelist(df_acc, count_fliter,
                              sum_fliter, percentage_fliter))
G.add_edges_from(get_edgelist(df_acc, count_fliter,
                              sum_fliter, percentage_fliter))

nx.graph_number_of_cliques(G)
partition = community.best_partition(G)

pos = nx.spring_layout(G)
plt.figure(figsize=(8, 8), dpi=72)
plt.axis('off')
nx.draw_networkx_nodes(G, pos, node_size=20,
                       cmap=plt.cm.RdYlBu, node_color=list(partition.values()))
nx.draw_networkx_edges(G, pos, alpha=0.3)

nx.write_gexf(G, r'E:\\research\\data\\圖庫\\test_4.gexf')
# plt.show(G)


# %%
clique = pd.DataFrame(
    [pd.Series(partition).index.tolist(), pd.Series(partition).tolist()]).T
clique.columns = ['com_User', 'user_Clique']
test_acc = get_fliterdata(df_acc, count_fliter, sum_fliter, percentage_fliter)
test_acc = pd.merge(test_acc, clique, 'left', 'com_User')   # ★第四條件篩選結果

#testdata.to_excel(r'E:\\research\\data\\網軍關係.xlsx', index=False)


# %%
set1 = set(test_ca['com_User'])
set2 = set(time_calist['com_User'])
set3 = set(test_acc['com_User'])


# %%
test_acc = test_acc[['user_Clique', 'com_User', 'post_Author']]
test_acc = pd.merge(test_acc, prefer_party(
    set(test_acc['com_User']), 'sum'), 'left', 'com_User')
test_acc = test_acc[['user_Clique', 'com_User',
                     'post_Author', 'Region', 'prefer_party']]
test_acc.dropna(inplace=True)
test_acc.reset_index(drop=True, inplace=True)

# %%
test_acc_cnt_region = test_acc.groupby(
    ['user_Clique', 'Region'], as_index=False)['com_User'].count()
test_acc_cnt_region_tomerge = test_acc_cnt_region.groupby(
    'user_Clique', as_index=False)['com_User'].sum()

test_acc_cnt_region = pd.merge(
    test_acc_cnt_region, test_acc_cnt_region_tomerge, 'left', 'user_Clique')
test_acc_cnt_region.columns = ['user_Clique', 'Region',	'com_User',	'com_User_sum']
test_acc_cnt_region['com_User_%'] = test_acc_cnt_region['com_User']/test_acc_cnt_region['com_User_sum']

cli_mask = (test_acc_cnt_region['com_User_sum'] >= 10) & (
    test_acc_cnt_region['com_User'] >= 5) & (test_acc_cnt_region['com_User_%']>=0.25)
test_acc_cnt_region = test_acc_cnt_region.loc[cli_mask]

test_acc_party = pd.merge(test_acc_cnt_region, test_acc, 'left', on=['user_Clique','Region'])
set4 = set(test_acc_party['com_User_y'])


# %%
test_acc_party.loc[(test_acc_party['com_User_y'].isin(set(set1 & set2 & set4)))].to_excel(path+'fin.xlsx',index=False)


# %%
