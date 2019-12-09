# %%
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
from tqdm import tqdm


# %%
'''
db_path = r'D:\\research\\data\\sql\\analysis.db'
with sqlite3.connect(db_path) as con:
    post = pd.read_sql('SELECT * FROM original_post', con)
    push = pd.read_sql('SELECT * FROM original_push', con)

df = pd.merge(post, push, 'left', 'post_ID')
'''
polarity = pd.read_excel(
    r'E:\\research\\data\\候選人資料\\polarity.xlsx')
polarity.dropna(inplace=True)
polarity = polarity[polarity['prefer_value'] > 10]
calist_1 = set(polarity['com_User'].tolist())

active = pd.read_excel(
    r'E:\\research\\data\\候選人資料\\活躍百分位數0.9_留言下限10則_文章不限單一候選人.xlsx')

# %%
ca = pd.merge(active, polarity, 'right', 'com_User')

# %%
ca.groupby(['Region_y','prefer'],as_index=False)[['com_User']].count()

# %%
