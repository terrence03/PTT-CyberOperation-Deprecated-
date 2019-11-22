# %%
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime
from tqdm import tqdm

# 讀取資料
with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
    df = pd.read_sql('SELECT 推文作者,文章ID,推文時間 FROM 推文資料', con=con)

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

# %%
# 整理資料


def get_index(df, col_name, text):
    result_list = df.index[df[col_name] == text].tolist()

    return result_list


df.drop(get_index(df, '推文時間', '2018/xx/xx '), inplace=True)  # 先移除遺漏資料
df.reset_index(drop=True, inplace=True)


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


df['time'] = get_ChangeDate(df['推文時間'])  # 將字串轉為時間資料
df.drop(get_index(df, 'time', 'N/A'), inplace=True)  # 移除無法被轉換的資料

# 設定時間範圍
start_date = datetime(2018, 6, 17)
end_date = datetime(2018, 11, 24)
mask = (df['time'] > start_date) & (df['time'] < end_date)
df = df.loc[mask]
df.reset_index(drop=True, inplace=True)


# 將提取時間中的星期和鐘點
df['weekday'] = df['time'].apply(lambda x: x.isoweekday())
df['worktime'] = df['time'].apply(lambda x: x.hour)


# %%
# 統計帳號留言時間分佈
weekday_cnt = df[['weekday', 'worktime']].groupby(
    ['weekday'], as_index=False).count()
weekday_cnt.rename(columns={'worktime': 'count'}, inplace=True)

worktime_cnt = df[['weekday', 'worktime']].groupby(
    ['worktime'], as_index=False).count()
worktime_cnt.rename(columns={'weekday': 'count'}, inplace=True)

# %%
# 繪圖顯示留言時間分佈
plt.figure(figsize=(10, 12))

# 上線星期
plt.subplot(2, 1, 1)

x_weekday = weekday_cnt['weekday']
y_weekday = weekday_cnt['count']
plt.plot(x_weekday, y_weekday, 'o-', label='count')
plt.xticks(range(1, 8))
plt.xlabel('Weekday')
plt.ylabel('Frequency')
plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
plt.title('Weekday')

# 上線時間
plt.subplot(2, 1, 2)

x_worktime = worktime_cnt['worktime']
y_worktime = worktime_cnt['count']

plt.plot(x_worktime, y_worktime, 'o-', label='count')
plt.xticks(range(24))
plt.xlabel('Time of Day')
plt.ylabel('Frequency')
plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
plt.title('Worktime')

plt.show()

# %%
