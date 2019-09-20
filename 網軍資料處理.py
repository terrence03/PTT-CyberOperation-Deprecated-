#%%
import sqlite3
import pandas as pd

with sqlite3.connect(r"D:\\research\\推文資料.sqlite") as con:
    df = pd.read_sql("SELECT * FROM 網軍測試", con = con)

data = df.drop_duplicates()    #刪除整個row重複

#%%
conn = sqlite3.connect(r"D:\\research\\死忠程度.db")
c = conn.cursor()
sql = "INSERT OR REPLACE INTO 網軍測試 (作者, 文章ID, 文章IP, 發文時間, 推文類型, 推文作者, 推文內文, 推文IP, 推文日期, 推文時間, 淨推數) VALUES (?,?,?,?,?,?,?,?,?,?,?)"

c.executemany(sql, data.to_records(index = False))
conn.commit()
conn.close()

#%%
grouped = data.groupby(['作者','推文作者'])
grouped_cnt = grouped['推文內文']
#計算某帳號在某作者文章下留言的次數
print(grouped_cnt.agg('count'))

#%%
'''
grouped_upv = data.groupby(['作者', '推文作者', '推文類型' == '推'])
grouped_upv_cnt = grouped['推文內文']
#計算某帳號在某作者文章下推的次數
#未完成，先擱置
'''

#%%
