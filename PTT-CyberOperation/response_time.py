# %%
from tqdm import tqdm
from datetime import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import sqlite3

db_path = r'D:\\research\\data\\sql\\analysis.db'
with sqlite3.connect(db_path) as con:
    post = pd.read_sql(
        'SELECT post_ID, Candidate, post_Title, post_Datetime FROM original_post', con)
    push = pd.read_sql(
        'SELECT post_ID, com_User, com_Datetime FROM original_push', con)

ca_data1 = pd.read_excel(
    r'E:\\research\\data\\候選人資料\\活躍百分位數0.9_留言下限10則_文章不限單一候選人.xlsx')
calist1 = set(ca_data1['com_User'].tolist())

polarity = pd.read_excel(
    r'E:\\research\\data\\候選人資料\\polarity.xlsx')
polarity.dropna(inplace=True)
ca_data2 = polarity[polarity['prefer_value'] > 10]
calist2 = set(ca_data2['com_User'].tolist())

post.dropna(inplace=True)
push.dropna(inplace=True)

post['post_Datetime'] = post['post_Datetime'].map(
    lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
push['com_Datetime'] = push['com_Datetime'].map(
    lambda x: datetime.strptime(x, '%Y/%m/%d %H:%M'))


# %%

keyword = pd.read_excel(
    r'E:\\research\\data\\候選人資料\\候選人關鍵字對照表.xlsx', '工作表1')  # 匯入候選人關鍵字對照表
candidate_list = keyword['候選人'].drop_duplicates().tolist()   # 建立候選人列表
candidate_list_in = post['Candidate'].drop_duplicates(
).tolist()  # 建立資料中出現過的候選人列表


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
    for i in range(len(post['keywords'])):
        if post.loc[i, 'keywords'] == '':
            post.loc[i, 'keywords'] = post.loc[i, 'Candidate']


post['keywords'] = get_keywords(post, 'post_Title')  # 建立關鍵字欄
fillkeywords()  # 填滿空的關鍵字欄

df = pd.merge(push, post, 'left', 'post_ID')


# %%
df_cal2 = df[df['com_User'].isin(calist2)]

response_time = df_cal2.groupby(
    ['com_User', 'post_ID', 'post_Datetime'], as_index=False)['com_Datetime'].min()
response_time['time_difference'] = (
    response_time['com_Datetime'] - response_time['post_Datetime'])
response_time['time_difference'] = response_time['time_difference'].map(
    lambda x: x.seconds/60)

mask = (response_time['time_difference'] <
        np.median(response_time['time_difference']))
response_time_ca = response_time.loc[mask]



# %%
ca_list = response_time_ca['com_User'].drop_duplicates().tolist()


# %%
def get_response_timedelta(DataFrame):
    response_time = DataFrame.groupby(
        ['com_User', 'post_ID', 'post_Datetime'], as_index=False)['com_Datetime'].min()
    response_time['time_difference'] = (
        response_time['com_Datetime'] - response_time['post_Datetime'])
    response_time['time_difference'] = response_time['time_difference'].map(
        lambda x: x.seconds/60)

    return response_time

df_response_time = get_response_timedelta(df)
# %%
