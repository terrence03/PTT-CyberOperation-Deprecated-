import sqlite3
import pandas as pd
import numpy as np
from tqdm import tqdm

#讀入資料
with sqlite3.connect(r'D:\\research\\推文資料.sqlite') as con:
    data = pd.read_sql_query("SELECT * FROM 推文資料", con = con)

conn = sqlite3.connect(r'D:\\research\\推文資料.sqlite')
c = conn.cursor()

#print(data.shape)
#print(data.dtypes)
#print(data.head())

rows = data.shape[0]

net_upvote = 0
net_dnvote = 0
for i in tqdm(range(rows)):
    if data.iloc[i][0] == data.iloc[i-1][0]:
        if data.iloc[i][2] == "推" :
            net_upvote = net_upvote + 1
            net_dnvote = net_dnvote - 1
        elif data.iloc[i][2] == "噓" :
            net_upvote = net_upvote - 1
            net_dnvote = net_dnvote + 1
        elif data.iloc[i][2] == "→":
            net_upvote = net_upvote
            net_dnvote = net_dnvote
        data.iloc[i][8] = net_upvote
        data.iloc[i][9] = net_dnvote
        #print("同文章")
    else:
        net_upvote = 0
        net_dnvote = 0
        if data.iloc[i][2] == "推":
            net_upvote = net_upvote + 1
            net_dnvote = net_dnvote - 1
        elif data.iloc[i][2] == "噓":
            net_upvote = net_upvote - 1
            net_dnvote = net_dnvote + 1
        elif data.iloc[i][2] == "→":
            net_upvote = net_upvote
            net_dnvote = net_dnvote
        data.iloc[i][8] = net_upvote
        data.iloc[i][9] = net_dnvote
        #print("不同文章")


sql = "INSERT OR REPLACE INTO 新推文資料 (文章ID, 候選人, 推文類型, 推文作者, 推文內文, 推文IP, 推文日期, 推文時間, 淨推數, 淨噓數) VALUES (?,?,?,?,?,?,?,?,?,?)"

c.executemany(sql, data.to_records(index=False))
conn.commit()
conn.close()

print("finish")
