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
# %%
data = data.groupby(['post_ID', 'post_Author', 'com_User'],
                    as_index=False)[['count']].count()
data['count_1'] = 1

sum_user2author = data.groupby(['com_User', 'post_Author'], as_index=False)[
    ['count_1']].sum()
sum_user = data.groupby('com_User', as_index=False)[['count_1']].sum()
# %%
sum_user = sum_user.loc[(sum_user['count_1'] > 1)]
ulist = sum_user['com_User'].tolist()
sum_user2author = sum_user2author.loc[(
    sum_user2author['com_User'].isin(ulist))]
# %%
accompany = pd.merge(sum_user2author, sum_user, 'left', 'com_User')
accompany['percentage'] = accompany['count_1_x']/accompany['count_1_y']
# %%
np.mean(accompany['percentage'])
np.median(accompany['percentage'])
stats.mode(accompany['percentage'])[0][0]

test1 = accompany.loc[(accompany['count_1_y'] >= 5)]
test2 = accompany.loc[(accompany['count_1_y'] >= 10)]
# %%
test1.loc[(test1['percentage'] >= 0.3)]
test2.loc[(test2['percentage'] >= 0.3)]
