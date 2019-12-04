# %%
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime
from tqdm import tqdm


# 讀取資料
with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
    # 推文資料
    df = pd.read_sql('SELECT 推文作者,文章ID,推文時間 FROM 推文資料', con=con)

    # 文章資料
    data = pd.read_sql('SELECT 作者,文章ID,發文時間 FROM 合併資料表', con=con).drop_duplicates()
    data.reset_index(drop=True, inplace=True)

'''
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
'''
# df['time'][0].time().hour


def get_index(DataFrame, col_name, text):
    result_list = DataFrame.index[DataFrame[col_name] == text].tolist()

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


def get_ChangeDate2(time_col):
    time_list = []
    for i in tqdm(range(len(time_col))):
        try:
            time = datetime.strptime(time_col[i], '%Y-%m-%d %H:%M:%S')
        except:
            time = 'N/A'

        time_list.append(time)

    return time_list


def daterange(DataFrame, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    mask = (DataFrame['time'] > start_date) & (DataFrame['time'] < end_date)
    
    return DataFrame.loc[mask]


# %%
# 整理推文資料


df.drop(get_index(df, '推文時間', '2018/xx/xx '), inplace=True)  # 先移除遺漏資料
df.reset_index(drop=True, inplace=True)


df['time'] = get_ChangeDate(df['推文時間'])  # 將字串轉為時間資料
df.drop(get_index(df, 'time', 'N/A'), inplace=True)  # 移除無法被轉換的資料



df = daterange(df, '2018-6-17', '2018-11-24')
df.reset_index(drop=True, inplace=True)
del df['推文時間']

df['state'] = 'comment'

# %%
# 整理文章資料


data['time'] = get_ChangeDate2(data['發文時間'])
data.drop(get_index(data, 'time', 'N/A'), inplace=True)

data = daterange(data, '2018-6-17', '2018-11-24')
data.reset_index(drop=True, inplace=True)
del data['發文時間']

data['stata'] = 'post'

# %%
# 合併推文和文章資料及保存


df.columns = ['Author', 'postID', 'time', 'state']
data.columns = ['Author', 'postID', 'time', 'state']

df = pd.concat([df, data])
df.sort_values('Author', inplace=True)
df.reset_index(drop=True, inplace=True)

#with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
#    df.to_sql('onlinetime', con=con, index=False)



# %%
# 統計帳號留言時間分佈

df['Weekday'] = df['time'].apply(lambda x: x.isoweekday())  # 提取星期和鐘點
df['Hour'] = df['time'].apply(lambda x: x.hour)


weekday_cnt = df[['Weekday', 'postID']].groupby(
    ['Weekday'], as_index=False).count()
weekday_cnt.rename(columns={'postID': 'count'}, inplace=True)

hour_cnt = df[['Hour', 'postID']].groupby(
    ['Hour'], as_index=False).count()
hour_cnt.rename(columns={'postID': 'count'}, inplace=True)

# %%
# 繪圖顯示留言時間分佈
plt.figure(figsize=(10, 12), dpi=300)

# 上線星期
plt.subplot(2, 1, 1)

x_weekday = weekday_cnt['Weekday']
y_weekday = weekday_cnt['count']
plt.plot(x_weekday, y_weekday, 'o-', label='count')
plt.xticks(range(1, 8))
plt.xlabel('Weekday')
plt.ylabel('Frequency')
plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
plt.title('Weekday')

# 上線時間
plt.subplot(2, 1, 2)

x_hour = hour_cnt['Hour']
y_hour = hour_cnt['count']

plt.plot(x_hour, y_hour, 'o-', label='count')
plt.xticks(range(24))
plt.xlabel('Time of Day')
plt.ylabel('Frequency')
plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
plt.title('Hour')

plt.savefig(r'E:\\research\\data\\圖庫\\frequency_all.png')
plt.show()

# %%
