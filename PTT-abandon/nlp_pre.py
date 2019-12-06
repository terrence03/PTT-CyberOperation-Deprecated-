# %%
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm
import sqlite3
import pandas as pd
import re
import os

path = 'E:\\research\\data\\sql'
file = 'data.db'

with sqlite3.connect(os.path.join(path, file)) as con:
    df = pd.read_sql(
        'SELECT 文章ID, 推文類型, 推文作者, 推文內文, 推文時間, 推文IP FROM 推文資料', con=con)

# %%
# 推文時間格式化


def get_index(df, col_name, text):
    result_list = df.index[df[col_name] == text].tolist()

    return result_list


def get_ChangeDate(time_col):
    time_list = []
    for i in tqdm(range(len(time_col))):
        try:
            time = datetime.strptime(time_col[i], '%Y/%m/%d %H:%M')
        except:
            time = 'N/A'

        time_list.append(time)

    return time_list
# get_ChangeDate()用來將字串的日期格式轉為datetime的格式
# 更好的方式應該用apply()，但原始資料中有些資料格式無法匹配，例如'2018/56/33 25:69'，所以改用迴圈的方式逐條轉化

df['time'] = get_ChangeDate(df['推文時間'])
df.drop(get_index(df, 'time', 'N/A'), inplace=True)


# 內文空格刪除
df['推文內文'] = df['推文內文'].map(lambda x: x.strip())

# 刪除時間不完整的資料
df['tc'] = df['推文時間'].map(lambda x: len(x))
df.drop(df.index[df['tc'] <= 11].tolist(), inplace=True)

# %%
# 觀察內文字數
'''
PTT推文字數限制：
PTT推文以行為單位，每一行的最大字數為80字（格）
如：    '噓 AGENTofAQUA: 憑我有腦袋，韓這貨跟蔡英文有什差別？？？一個用愛   11/13 11:43'
推文類型（2）+空格（1）+作者ID（？）+：（1）+空格（1）+推文內文（？）+空格（2）+IP（?）+空格（1）+日期（5）+空格（1）+時間（5）+空格（2）
除了作者ID、推文內文以及IP外，其他內容都是保留字，每則推文都會保留這些格位，共18格
扣除保留格位，作者ID、推文內文以及IP的字數總和必須在45字內
若ID較長，就會壓縮到內文的空間
*中文字算做 2格
'''


def len_by_utf8(x):
    c = 0
    # 中文字在utf-8中占3 bytes，但PTT網頁中是2 bytes，所以需要將3 bytes轉換成2 bytes
    # 原本使用big5編碼的話中文就會占2 bytes，但經過測試，有部分文字無法轉為big5
    for i in range(len(x)):
        code = len(x[i].encode('utf-8'))
        if code == 3:
            code = 2
        else:
            code = code
        c = c + code

    return c


df['a_cnt'] = df['推文作者'].map(lambda x: len(x))
df['c_cnt'] = df['推文內文'].apply(lambda x: len_by_utf8(x))
df['i_cnt'] = df['推文IP'].map(lambda x: len(x))
df['a+c_cnt'] = df['a_cnt'] + df['c_cnt']
df['t_cnt'] = df['a_cnt'] + df['c_cnt'] + df['i_cnt']

# df.drop(df.index[df['t_cnt'] > 60].tolist(), inplace=True)

# %%
# 顯示字數統計（推文作者+推文內文+推文IP），最小值為3，最大值為60
matplotlib.rcParams['font.sans-serif'] = ['SimHei']   # 用黑體顯示中文

plt.hist(df['a+c_cnt'],
         bins=range(max(df['a+c_cnt'])+1),
         facecolor="white",
         edgecolor="black",
         color='white',
         alpha=1)

plt.xlabel('字數')
plt.ylabel('出現次數')
plt.title('推文字數統計')



# %%
df['推文內文'][2870492]
# %%
