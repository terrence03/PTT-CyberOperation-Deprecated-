# %%
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
    df = pd.read_sql(
        'SELECT Author,postID, time, Weekday, Hour FROM onlinetime', con)


pd.set_option('precision', 3)

# %%
W_dummy = pd.get_dummies(df[['Author', 'Weekday']]
                         ['Weekday'], prefix='Weekday')
df_W = df[['Author']].join(W_dummy)
df_W_group = df_W.groupby(['Author'], as_index=False)

df_W_sum = df_W_group.sum()
df_W_sum[df_W_sum.columns[1:8].tolist(
)] = df_W_sum[df_W_sum.columns[1:8].tolist()].astype('int')

df_W_sum['sum'] = df_W_sum.sum(axis=1).astype('int')

df_W_precentage = df_W_group.mean()
# %%
H_dummy = pd.get_dummies(df[['Author', 'Hour']]['Hour'], prefix='Hour')
df_H = df[['Author']].join(H_dummy)
df_H_group = df_H.groupby(['Author'], as_index=False)

df_H_sum = df_H_group.sum()
df_H_sum[df_H_sum.columns[1: 25].tolist()] = df_H_sum[df_H_sum.columns[1: 25].tolist()].astype('int')

df_H_sum['sum'] = df_H_sum.sum(axis=1).astype('int')

df_H_precentage = df_H_group.mean()

# %%
mask = (df_H_precentage['Hour_14'] > 0.1)
#df_H_precentage.loc[mask]

A_list = df_H_precentage.loc[mask][['Author']]
A_list = pd.merge(A_list, df_H_sum, how='left', on='Author')
del A_list['sum']


# %%
list1 = []
for i in range(1, 25):
    col = A_list.columns.tolist()[i]
    su = A_list[col].sum()
    list1.append(su)


# %%
plt.figure(figsize=(10, 6), dpi=72)
x = list(range(24))
y = list1
plt.plot(x, y, 'o-', label='count')


# %%
def clean_namelist(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        result = file.read()

    result = result.replace('\n', ',').replace('、', ',').replace('.', ',')
    namelist = result.split(',')

    for i in range(len(namelist)):
        namelist[i] = namelist[i].strip()

    namelist = ' '.join(namelist).replace('  ', ' ')
    namelist = namelist.split(' ')

    namelist1 = []
    for j in range(len(namelist)):
        if namelist[j] != '':
            namelist1.append(namelist[j])

    return namelist1


namelist = pd.DataFrame(clean_namelist(r'E:\\research\\data\\砍除帳號名單.txt'), columns=['Author'])

# %%
df_namelist = pd.merge(namelist, df, how='left', on='Author')
df_namelist.dropna(inplace=True)


weekday_cnt = df_namelist[['Weekday', 'postID']].groupby(
    ['Weekday'], as_index=False).count()
weekday_cnt.rename(columns={'postID': 'count'}, inplace=True)

hour_cnt = df_namelist[['Hour', 'postID']].groupby(
    ['Hour'], as_index=False).count()
hour_cnt.rename(columns={'postID': 'count'}, inplace=True)

# %%
plt.figure(figsize=(10, 12), dpi=300)

plt.subplot(2,1,1)

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

plt.savefig(r'E:\\research\\data\\圖庫\\frequency_ca.png')
plt.show()


# %%
