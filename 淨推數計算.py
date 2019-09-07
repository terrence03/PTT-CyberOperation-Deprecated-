import sqlite3
import pandas as pd
from tqdm import tqdm

#讀入資料
with sqlite3.connect(r'D:\\research\\推文資料.sqlite') as con:
# read_sql_query和read_sql都能通過SQL語句從資料庫檔案中獲取資料資訊
    data = pd.read_sql_query("SELECT * FROM 推文資料", con = con)
# df = pd.read_sql("SELECT * FROM test_table", con=con)

#print(data.shape)
#print(data.dtypes)
#print(data.head())
