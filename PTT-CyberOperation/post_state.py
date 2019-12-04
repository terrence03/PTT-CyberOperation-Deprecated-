# %%
from snownlp import SnowNLP
import re
from tqdm import tqdm
from datetime import datetime
import pandas as pd
import sqlite3
import numpy as np

path = r'E:\\research\\data\\sql\\'
file = 'data.db'
with sqlite3.connect(path + file) as con:
    sql = 'SELECT 候選人,關鍵字,文章ID,作者,文章標題,文章內文,發文時間,文章IP FROM allpost'
    df = pd.read_sql(sql, con)
    df.columns = ['candidate', 'keyword', 'postID',
                  'Author', 'title', 'content', 'time', 'IP']
# %%
df['datetime'] = df['time'].map(
    lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
del df['time']
# %%
candidate = df['candidate'].drop_duplicates().tolist()
keyword = df['keyword'].drop_duplicates().tolist()

KW = []
for i in tqdm(range(len(df['title']))):
    kwlist = []
    for j in range(len(keyword)):
        if keyword[j] in df['title'][i]:
            kwlist.append(keyword[j])
        kw = ','.join(kwlist)
    KW.append(kw)

df['keywords'] = KW

# %%
categroy = ['[新聞]', '[問卦]', '[爆卦]', '[轉錄]', '[ＦＢ]', 'Fw:']

# 排除回文
mask = (df['title'].str.match('^Re'))
data = df.loc[~mask]

data.reset_index(drop=True, inplace=True)
# %%


def get_lenkeywordlist(keyword_list):
    keyword_list = keyword_list.tolist()
    kl = []
    for i in range(len(keyword_list)):
        kr = len(keyword_list[i].split(','))
        kl.append(kr)
    return kl


def split_keywords(DataFrame, keyword_col):
    kc = DataFrame[keyword_col]
    mxlnc = max(get_lenkeywordlist(kc))
    milnc = min(get_lenkeywordlist(kc))

    for i in range(milnc, mxlnc+1):
        colname = 'keyword' + str(i)
        DataFrame[colname] = np.nan

        for j in range(len(kc)):
            if len(kc[j].split(',')) >= i:
                DataFrame[colname][j] = kc[j].split(',')[i-1]


split_keywords(data, 'keywords')


# %%
mask = (data['title'].str.match('^\[問卦\]|^\[爆卦\]'))
test_data = data.loc[mask]

test_data['sentiment'] = test_data['content'].apply(
    lambda x: SnowNLP(x).sentiments)

# %%
with sqlite3.connect(path + file) as con:
    sql = 'SELECT 文章ID,推文類型,推文作者,推文內文,推文IP,推文時間 FROM 推文資料'
    data = pd.read_sql(sql,con)
    data.columns = ['postID','com_Type','com_User','com_Content','com_IP','com_Time']
# %%
df.columns = ['region','candidate',	'n_post','keyword','postID','post_Author','post_Title','post_Content','post_IP','post_Datetime','keywords']

data1 = pd.merge(df, data, how='left', on='postID')
data1 = data1[['region','candidate','keywords','postID','post_Author','post_Title','post_IP','post_Datetime','com_Type','com_User','com_Content','com_IP','com_Time','n_post']]
# %%
with sqlite3.connect(path + 'analysis.db') as con:
    data1.to_sql('original_data',con,index=False)


# %%
