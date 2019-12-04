# %%
import re
from tqdm import tqdm
from datetime import datetime
import pandas as pd
import sqlite3
import numpy as np

path = r'D:\\research\\data\\sql\\'
file = 'analysis.db'
with sqlite3.connect(path + file) as con:
    sql = 'SELECT * FROM original_data'
    df = pd.read_sql(sql,con)

# %%
# 1. 淨推數計算
'''
PTT的淨推數是吸引用戶點入閱讀的因素之一
但爬資料時無法收錄每個時間的淨推數,需要在資料中重現

淨推數 = 總推文數 - 總噓文數, 淨推數的上限為100
當淨推數 = 100時增加一則推文, 淨推數維持100
當淨推數 = 100時增加一則噓文, 淨推數變為99

ps.淨推數需要先行計算, 避免後續data missing需要刪除資料時, 重現淨推數會出現誤差
'''
def get_grosspush(DataFlame, push_Type_col):
    data = DataFlame[push_Type_col]
    rows = data.shape[0]

    count_list = []
    net_upvote = 0
    for i in tqdm(range(rows)):
        if data.iloc[i, 0] == data.iloc[i-1, 0]:
            if data.iloc[i, 5] == "推":
                net_upvote = net_upvote + 1
            elif data.iloc[i, 5] == "噓":
                net_upvote = net_upvote - 1
            elif data.iloc[i, 5] == "→":
                net_upvote = net_upvote
            count_list.append(net_upvote)

            # print("同文章")
        else:
            net_upvote = 0

            if data.iloc[i, 5] == "推":
                net_upvote = net_upvote + 1
            elif data.iloc[i, 5] == "噓":
                net_upvote = net_upvote - 1
            elif data.iloc[i, 5] == "→":
                net_upvote = net_upvote
            count_list.append(net_upvote)

            # print("不同文章")
    data['淨推數'] = count_list
