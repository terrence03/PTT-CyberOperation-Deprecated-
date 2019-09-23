#%%
import sqlite3
import pandas as pd

def movedata():
    with sqlite3.connect(r'D:\\research\\data.db') as con:
        df = pd.read_sql('SELECT * FROM 合併資料表', con = con).drop_duplicates('文章ID')

    conn = sqlite3.connect(r'D:\\research\\選舉研究\\data.db')
    c = conn.cursor

    sql = 'INSERT INTO 合併資料表(候選人,關鍵字,文章ID,作者,文章標題,發文時間,文章IP,留言數,文章內文,推文列表) VALUES(?,?,?,?,?,?,?,?,?,?)'
    conn.executemany(sql, df.to_records(index=False))
    conn.commit()
    conn.close()

#%%
with sqlite3.connect(r'D:\\research\\選舉研究\\data.db') as con:
    df = pd.read_sql('SELECT * FROM 合併資料表', con = con)

#%%
rows = []
for i in range(len(df['發文時間'])):
    if df.iloc[i, 5] == 0:
        rows.append(i)

df_clean = df.drop(rows)

conn = sqlite3.connect(r'D:\\research\\選舉研究\\data.db')
c = conn.cursor

sql = 'INSERT INTO 合併資料表_new (候選人,關鍵字,文章ID,作者,文章標題,發文時間,文章IP,留言數,文章內文,推文列表) VALUES(?,?,?,?,?,?,?,?,?,?)'
conn.executemany(sql, df.to_records(index=False))
conn.commit()
conn.close()
#%%
#使用已清理好的作者資料
with sqlite3.connect(r'D:\\research\\推文資料.sqlite') as con:
    author_list = pd.read_sql('SELECT * FROM 作者名單', con=con)

df1 = pd.merge(df, author_list, on = '文章ID', how = 'outer')

#%%
