#%%
import sqlite3
import pandas as pd

with sqlite3.connect(r"D:\\research\\推文資料.sqlite") as con:
    df = pd.read_sql("SELECT * FROM 結合資料_新", con = con)

data = df.drop_duplicates()    #刪除整個row重複

#%%
conn = sqlite3.connect(r"D:\\research\\死忠程度.db")
c = conn.cursor()
sql = "INSERT OR REPLACE INTO 網軍測試 (作者, 文章ID, 文章IP, 發文時間, 推文類型, 推文作者, 推文內文, 推文IP, 推文日期, 推文時間, 淨推數) VALUES (?,?,?,?,?,?,?,?,?,?,?)"

c.executemany(sql, data.to_records(index = False))
conn.commit()
conn.close()

#%%
#計算某帳號在某作者文章下留言的次數
grouped_1 = data.groupby(['作者','推文作者'], as_index = False)['推文內文']

#%%
#計算留言帳號在每個作者下留言的機率
grouped_2 = data.groupby(['推文作者','作者'], as_index = False)['推文內文']
com = grouped_2.agg({'cnt': 'count'})

sum_com = com.groupby(['推文作者'], as_index = False)['cnt'].agg({'sum':'sum'})
cross_com = pd.merge(com, sum_com)
cross_com['留言機率'] = cross_com['cnt']/cross_com['sum']

#%%
#計算推文帳號在每個作者下推文的機率
grouped_vpv = data[data['推文類型'] == '推']
grouped_2 = grouped_vpv.groupby(['推文作者', '作者'], as_index=False)['推文內文']
com = grouped_2.agg({'cnt': 'count'})

sum_com = com.groupby(['推文作者'], as_index=False)['cnt'].agg({'sum': 'sum'})
cross_com = pd.merge(com, sum_com)
cross_com['留言機率'] = cross_com['cnt']/cross_com['sum']

#%%
