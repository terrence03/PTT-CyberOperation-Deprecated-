# %%
from pylab import mpl
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

with sqlite3.connect(r'E:\\research\\data\\data\\data.db') as con:
    df = pd.read_sql(
        'SELECT Author,postID, time, Weekday, Hour FROM onlinetime', con)


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
df_H_sum[df_H_sum.columns[1: 25].tolist(
)] = df_H_sum[df_H_sum.columns[1: 25].tolist()].astype('int')

df_H_sum['sum'] = df_H_sum.sum(axis=1).astype('int')

df_H_precentage = df_H_group.mean()

# %%

def get_H_avgprecentage(DataFrame):
    h = 'Hour_'
    n = list(range(0, 24))

    avg_precentage_value = []
    for c in range(24):
        cc = h + str(n[c])
        avg_precentage_value.append(DataFrame[cc].mean())

    return avg_precentage_value


def get_W_avgprecentage(DataFrame):
    w = 'Weekday_'
    n = list(range(1, 8))

    avg_precentage_value = []
    for c in range(7):
        cc = w + str(n[c])
        avg_precentage_value.append(DataFrame[cc].mean())

    return avg_precentage_value


# %%
# 加入網軍名單
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


#namelist = pd.DataFrame(clean_namelist(
#    r'E:\\research\\data\\砍除帳號名單.txt'), columns=['Author'])
namelist = pd.read_excel(r'E:\\research\\df.xlsx', sheet_name='Sheet1')
namelist = set(namelist['com_User'])|set(namelist['post_Author'])
namelist = pd.DataFrame(namelist)
namelist.columns = ['Author']

df_W_precentage_cy = pd.merge(
    namelist, df_W_precentage, how='left', on='Author')
df_W_precentage_cy.dropna(inplace=True)

df_H_precentage_cy = pd.merge(
    namelist, df_H_precentage, how='left', on='Author')
df_H_precentage_cy.dropna(inplace=True)

# %%
mpl.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 指定默认字体

fig = plt.figure(figsize=(8, 12), dpi=300)

plt.subplot(2,1,1)
plt.plot(list(range(1, 8)), get_W_avgprecentage(
    df_W_precentage_cy), 'o-', label='網軍', color='blue')
plt.plot(list(range(1,8)), get_W_avgprecentage(
    df_W_precentage), 's--', label='一般用戶', color='orange')

plt.legend()
plt.xticks(range(1,8))
plt.xlabel('星期', fontsize=12)
plt.ylabel('頻率百分比', fontsize=12)
plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
plt.title('網軍每天上線頻率', fontsize=15)
#plt.savefig(r'E:\\research\\data\\圖庫\\frequency_vs_3_1.png')

plt.subplot(2,1,2)
plt.plot(list(range(24)), get_H_avgprecentage(
    df_H_precentage_cy), 'o-', label='網軍', color='blue')
plt.plot(list(range(24)), get_H_avgprecentage(
    df_H_precentage), 's--', label='一般用戶', color='orange')

plt.legend()
plt.xticks(range(24))
plt.xlabel('時間', fontsize=12)
plt.ylabel('頻率百分比', fontsize=12)
plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
plt.title('網軍每小時上線頻率', fontsize=15)

plt.savefig(r'E:\\research\\data\\圖庫\\frequency_vs_3_4.png')
plt.show()

# %%
