# %%
# 匯入套件
import seaborn as sns
from matplotlib import pyplot as plt
import sqlite3
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import re
import numpy as np

# 匯入文章資料
#data_path = r'D:\\research\\data\\sql\\analysis.db'
data_path = r'D:\\研究\\選舉研究\\analysis.db'
#data_path_kw = r'E:\\research\\data\\候選人資料\\候選人關鍵字對照表.xlsx'
data_path_kw = r'D:\\研究\\選舉研究\\資料\\候選人資料\\候選人關鍵字對照表.xlsx'

with sqlite3.connect(data_path) as con:
    df = pd.read_sql('SELECT * FROM original_post', con)

df['post_Datetime'] = df['post_Datetime'].map(
    lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))    # 時間轉為datetime格式

keyword = pd.read_excel(data_path_kw, '工作表1')  # 匯入候選人關鍵字對照表
candidate_list = keyword['候選人'].drop_duplicates().tolist()   # 建立候選人列表
candidate_list_in = df['Candidate'].drop_duplicates(
).tolist()  # 建立資料中出現過的候選人列表

# %%


def get_keywords(DataFrame, title_col):
    '''
    取得DataFrame[title_col]所包含的候選人關鍵字的列表
    '''
    key_dict = {}
    for key, value in zip(keyword['關鍵字'], keyword['候選人']):
        key_dict[key] = value

    key = list(key_dict.keys())
    value = list(key_dict.values())
    data = DataFrame[title_col]

    KW = []
    for i in tqdm(range(len(data))):
        kwlist = []
        for j in range(len(key_dict)):
            if key[j] in DataFrame.loc[i, title_col]:
                kwlist.append(value[j])
            kw = ','.join(set(kwlist))
        KW.append(kw)

    return KW


def fillkeywords():
    '''
    將空的關鍵字欄填上候選人
    '''
    for i in range(len(df['keywords'])):
        if df.loc[i, 'keywords'] == '':
            df.loc[i, 'keywords'] = df.loc[i, 'Candidate']


df['keywords'] = get_keywords(df, 'post_Title')  # 建立關鍵字欄
fillkeywords()  # 填滿空的關鍵字欄

# %%
# 匯入留言資料
with sqlite3.connect(data_path) as con:
    data = pd.read_sql('SELECT * FROM original_push', con)
    data = pd.merge(df, data, 'left', 'post_ID')    # 將文章資料和留言資料結合


# %%
# 資料集概要
def get_candidate_post(candidate):
    '''
    填入一個候選人

    取得該候選人的[候選人名稱, 文章作者數, 文章數, 留言者數, 留言數]
    '''
    if candidate in candidate_list_in:
        select = (data['keywords'].str.contains(candidate))
        d = data.loc[select]
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


def candidate_post():
    '''
    將全部候選人填入get_candidate_post()中

    取得一個資料集概要的DateFrame
    '''
    summary = []
    for i in tqdm(range(len(candidate_list))):
        summary.append(get_candidate_post(candidate_list[i]))

    return pd.DataFrame(summary)


candidate_data = candidate_post()  # 建立資料集概要
candidate_data.columns = ['Candidate', 'post_Author',
                          'post_ID', 'com_User', 'com_Content']  # 資料集概要欄命名

# %%


def get_quantile_from_candidate(candidate, quantile, lower_limit=0):
    '''
    candidate: 填入一個候選人

    quantile: 填入百分位數的list

    lower_limit: 設定留言數下限，低於此數則不列入計算，預設為0

    取得一個候選人的留言數在某百分位數下的留言數
    '''
    if candidate in candidate_list_in:
        select = (data['keywords'].str.contains(candidate))
        d = data.loc[select]
        c = d.groupby('com_User', as_index=False)[['com_Content']].count()
        g = c.loc[(c['com_Content'] >= lower_limit)]
        q = g['com_Content'].quantile(quantile)
        ca = g.loc[(g['com_Content'] >= q)]
        ca['Candidate'] = candidate

    else:
        na = {'com_User': np.nan, 'com_Content': np.nan, 'Candidate': candidate}
        ca = pd.DataFrame(na, [0])

    return ca



CyberArmy80 = None
for c in candidate_list:
    CyberArmy80 = pd.concat([CyberArmy80, get_quantile_from_candidate(c, 0.8, 10)])

    # CyberArmy90['Region'] = CyberArmy90['Candidate'].map(lambda x: area_dict[x])
CyberArmy80 = CyberArmy80[['Candidate', 'com_User', 'com_Content']]


'''
area = pd.read_excel(r'E:\\research\\data\\候選人資料\\候選人地區.xlsx')
area_dict = {}
  for name, region in zip(area['姓名'], area['地區']):
    area_dict[name] = region
'''
# %%
data_1 = data[['keywords', 'com_Type', 'com_User']]
data_1.dropna(inplace=True)
Type = {'推': 1, '→': 0, '噓': -1}
data_1['com_Type'] = data_1['com_Type'].map(lambda x: Type[x])
# %%


def get_Polarity(text):
    candidate = text.split(',')[0]
    user = text.split(',')[1]
    select = (data_1['com_User'] == user) & (
        data_1['keywords'].str.contains(candidate))
    d = data_1.loc[select]
    polarity = d['com_Type'].sum()

    return polarity


# %%
CyberArmy80.dropna(inplace=True)
CyberArmy80['text'] = CyberArmy80['Candidate'] + ',' + CyberArmy80['com_User']
CyberArmy80['Polarity'] = CyberArmy80['text'].apply(lambda x: get_Polarity(x))

del CyberArmy80['text']


# %%
