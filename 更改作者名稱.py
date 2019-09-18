import sqlite3
import pandas as pd
from tqdm import tqdm

with sqlite3.connect(r"D:\\research\\推文資料.sqlite") as con:
    df = pd.read_sql("SELECT * FROM 作者資料", con = con)

conn = sqlite3.connect(r'D:\\research\\推文資料.sqlite')
c = conn.cursor()

#print(df.head())
#print(type(df.iloc[0][2]))

#pd.set_option('mode.chained_assignment', None)

rows = df.shape[0]

for i in tqdm(range(rows)):
    string = str(df.iloc[i][1])
    author = string.split("(")
    df.loc[i, "改作者"] = author[0]

sql = "INSERT OR REPLACE INTO 新作者資料 (文章ID, 作者, 改作者) VALUES (?,?,?)"

c.executemany(sql, df.to_records(index=False))
conn.commit()
conn.close()