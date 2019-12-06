# %%
import pandas as pd
import sqlite3
from snownlp import SnowNLP

path = r'E:\\research\\data\\sql\\'
file = 'data.db'
with sqlite3.connect(path + file) as con:
    sql = 'SELECT 候選人,關鍵字,文章ID,作者,文章標題,文章內文,發文時間,文章IP FROM allpost'
    df = pd.read_sql(sql, con)
    df.columns = ['candidate', 'keyword', 'postID',
                  'Author', 'title', 'content', 'time', 'IP']

# %%
