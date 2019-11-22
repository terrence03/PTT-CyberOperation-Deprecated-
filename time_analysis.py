# %%
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime
from tqdm import tqdm

with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
    df = pd.read_sql('SELECT 推文作者,文章ID,推文時間 FROM 推文資料', con=con)


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


time_section = {0: '00~03',  1: '00~03',  2: '00~03',
                3: '03~06',  4: '03~06',  5: '03~06',
                6: '06~09',  7: '06~09',  8: '06~09',
                9: '09~12', 10: '09~12', 11: '09~12',
                12: '12~15', 13: '12~15', 14: '12~15',
                15: '15~18', 16: '15~18', 17: '15~18',
                18: '18~21', 19: '18~21', 20: '18~21',
                21: '21~24', 22: '21~24', 23: '21~24', }

worktime = {0: '0',  1: '0',  2: '0',
            3: '0',  4: '0',  5: '0',
            6: '0',  7: '0',  8: '1',
            9: '1', 10: '1', 11: '1',
            12: '1', 13: '1', 14: '1',
            15: '1', 16: '1', 17: '1',
            18: '0', 19: '0', 20: '0',
            21: '0', 22: '0', 23: '0', }

# df['time'][0].time().hour

# %%
df.drop(get_index(df, '推文時間', '2018/xx/xx '), inplace=True)
df.reset_index(drop=True, inplace=True)

df['time'] = get_ChangeDate(df['推文時間'])
df.drop(get_index(df, 'time', 'N/A'), inplace=True)

df['weekday'] = df['time'].apply(lambda x: x.isoweekday())
# isoweekday()可以回傳該日期是星期幾，星期一回傳 1 ，星期天回傳 7

#df['時間段'] = df['time'].apply(lambda x: time_section[x.time().hour])
df['worktime'] = df['time'].apply(lambda x: worktime[x.time().hour])


#df = df.set_index(df['time'])

# %%
df.reset_index(drop=True, inplace=True)
df.columns = ['pushAuthor', 'postID', 'pushtime',
              'time', 'weekday', 'worktime']

df_le = df[['pushAuthor', 'postID', 'weekday', 'worktime']]
#dummy_timerange = pd.get_dummies(df_le['timerange'])
#dummy_weekday = pd.get_dummies(df_le['weekday'])
df_le = pd.get_dummies(df_le, columns=['worktime'])

# %%
df_ts = df[['pushAuthor', 'time']]
#df_ts['ts'] = df_ts['time'].apply(lambda x: x.time())
df_ts.set_index(df_ts['time'], inplace=True)

with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
    df_ts.to_sql('推文時間序列', index=False, con=con)

#ts_count = df_ts['pushAuthor'].resample('H', kind='timestamp').count()
# ts_count.plot()
# %%
