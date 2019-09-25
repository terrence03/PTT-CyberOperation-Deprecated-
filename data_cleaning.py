#%%
import sqlite3
import pandas as pd
from tqdm import tqdm
import re

#%%
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
    df = pd.read_sql('SELECT * FROM 合併資料表_測試', con = con)

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
#切分推文列表
rows = df.shape[0]
name1 = ['候選人', '關鍵字', '文章ID', '作者', '文章標題', '發文時間', '文章IP', '文章內文', '推文列表']
resultlist1 = []

for i in tqdm(range(rows)):
    candidate = df.iloc[i, 0]
    keyword = df.iloc[i, 1]
    post_ID = df.iloc[i, 2]
    author = df.iloc[i, 3]
    post_title = df.iloc[i, 4]
    post_time = df.iloc[i, 5]
    post_IP = df.iloc[i, 6]
    post_comment = df.iloc[i, 8]
    string = str(df.iloc[i, 9])
    comment_string = string.split('\n')

    for j in range(len(comment_string)):
        if comment_string[j].startswith('推 '):
            list1 = [candidate, keyword, post_ID, author, post_title,
                     post_time, post_IP, post_comment, comment_string[j]]
            resultlist1.append(list1)
        elif comment_string[j].startswith('噓 '):
            list2 = [candidate, keyword, post_ID, author, post_title,
                     post_time, post_IP, post_comment, comment_string[j]]
            resultlist1.append(list2)
        elif comment_string[j].startswith('→ '):
            list3 = [candidate, keyword, post_ID, author, post_title,
                     post_time, post_IP, post_comment, comment_string[j]]
            resultlist1.append(list3)

data = pd.DataFrame(resultlist1)
data.columns = name1

#%%
#切分推文內容
"""
此程式將每則推文的資訊切分出：
推文類型，推文作者，推文內容，推文IP，推文時間
"""

#根據測試，推文中有部分內容查無":"字元，這些推文會導致
error_rows = []
for x in range(data.shape[0]):
    if re.search(':', data.iloc[x, 8]) == None:
        error_rows.append(x)

data.drop(error_rows, inplace = True)

#%%
name2 = ['推文類型', '推文作者', '推文內文', '推文IP', '推文時間']
resultlist2 = []

for row in tqdm(range(data.shape[0])):
    string1 = data.iloc[row, 8]
    string_cut1 = re.split(' ', string1, 1)
    string_cut2 = re.split(':', string_cut1[1], 1)

    #推文類型
    push_type = string1[0]

    #推文作者
    push_author = re.split("[^a-zA-Z0-9]+", string_cut1[1], 1)[0]

    #推文內文
    if push_author != "":
        push_comment = re.sub(
            "(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])|(\d{2})/(\d{2})|(\d{2}):(\d{2})", "", string_cut2[1]).lstrip()
    else:
        push_comment = re.sub(
            "(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])|(\d{2})/(\d{2})|(\d{2}):(\d{2})", "", string_cut1[1]).lstrip()
    #取出內文的方式是將原字串中,類似IP,日期時間的字串取代成""(意思就是刪除)

    #推文IP
    if re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', string_cut1[1]) != None:
        push_IP = re.search(
            r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', string_cut1[1]).group()
    else:
        push_IP = ""

    #推文時間
    if re.search(r"(\d{2}):(\d{2})", string_cut1[1]) != None:
        time = re.search(r"(\d{2}):(\d{2})", string_cut1[1]).group()
    else:
        time = ""

    if re.search(r"(\d{2})/(\d{2})", string_cut1[1]) != None:
        date = re.search(r"(\d{2})/(\d{2})", string_cut1[1]).group()
    else:
        date = ""

    if date != "":
        push_time = str('2018/' + date + " " + time)
    else:
        push_time = str('2018/xx/xx' + " " + time)
    
    result = [push_type, push_author, push_comment, push_IP, push_time]
    resultlist2.append(result)

#新建一個DataFrame
data_plus = pd.DataFrame(resultlist2)
data_plus.columns = name2
#%%
