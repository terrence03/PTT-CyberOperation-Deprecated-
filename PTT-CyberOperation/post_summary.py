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
with sqlite3.connect(r'D:\\research\\data\\sql\\analysis.db') as con:
    df = pd.read_sql('SELECT * FROM original_post', con)

df['post_Datetime'] = df['post_Datetime'].map(
    lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))    # 時間轉為datetime格式

keyword = pd.read_excel(
    r'E:\\research\\data\\候選人資料\\候選人關鍵字對照表.xlsx', '工作表1')  # 匯入候選人關鍵字對照表
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
with sqlite3.connect(r'D:\\research\\data\\sql\\analysis.db') as con:
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


def get_CyberArmy90():
    CyberArmy90 = None
    for i in candidate_list:
        CyberArmy90 = pd.concat(
            [CyberArmy90, get_quantile_from_candidate(i, 0.9, 10)])

    # CyberArmy90['Region'] = CyberArmy90['Candidate'].map(lambda x: area_dict[x])
    CyberArmy90 = CyberArmy90[['Candidate', 'com_User', 'com_Content']]

    return CyberArmy90


'''
area = pd.read_excel(r'E:\\research\\data\\候選人資料\\候選人地區.xlsx')
area_dict = {}
  for name, region in zip(area['姓名'], area['地區']):
    area_dict[name] = region
'''
CyberArmy90 = get_CyberArmy90()
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
CyberArmy90.dropna(inplace=True)
CyberArmy90['text'] = CyberArmy90['Candidate'] + ',' + CyberArmy90['com_User']
CyberArmy90['Polarity'] = CyberArmy90['text'].apply(lambda x: get_Polarity(x))

#del CyberArmy90['text']
# %%
CyberArmy90_tpe = CyberArmy90[CyberArmy90['Region'] == '臺北市']


# %%
trans_data_Ko = CyberArmy90_tpe[CyberArmy90_tpe['Candidate'] == '柯文哲'][['com_Content','Polarity']]
sns.regplot('com_Content', 'Polarity', trans_data_Ko, color='r',)
plt.title('Ko')

# %%
x = trans_data_Ko['com_Content']
y = trans_data_Ko['Polarity']
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
#sns.regplot('com_Content', 'Polarity', trans_data, color='r',)
plt.plot(x, p(x), 'b--')
plt.scatter(x, y, alpha=0.6)
plt.title('Ko')
plt.show()


# %%
trans_data_Yao = CyberArmy90_tpe[CyberArmy90_tpe['Candidate'] == '姚文智'][[
    'com_Content', 'Polarity']]
sns.regplot('com_Content', 'Polarity', trans_data_Yao, color='r',)
plt.title('Yao')

# %%
x = trans_data_Yao['com_Content']
y = trans_data_Yao['Polarity']
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
#sns.regplot('com_Content', 'Polarity', trans_data, color='r',)
plt.plot(x, p(x), 'b--')
plt.scatter(x, y, alpha=0.6)
plt.title('Yao')
plt.show()

# %%
trans_data_Ting = CyberArmy90_tpe[CyberArmy90_tpe['Candidate'] == '丁守中'][[
    'com_Content', 'Polarity']]
sns.regplot('com_Content', 'Polarity', trans_data_Ting, color='r',)
plt.title('Ting')

# %%
x = trans_data_Ting['com_Content']
y = trans_data_Ting['Polarity']
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
#sns.regplot('com_Content', 'Polarity', trans_data, color='r',)
plt.plot(x, p(x), 'b--')
plt.scatter(x, y, alpha=0.6)
plt.title('Yao')
plt.show()


# %%
