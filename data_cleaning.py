#%%
# 匯入套件
import sqlite3
import pandas as pd
from tqdm import tqdm
import re

#%%
'''
以下問題會在程式中處理
1. 文章ID重複
2. 文章標題的資料遺漏（通常情況是該欄位的值是None）
3. 發文時間的資料遺漏（通常情況是該欄位的值是#N/A）
4. 作者的資料常常包含換行、特殊符號
5. 作者的欄位有文章的內文
6. 推文列表的欄位有文章的內文

原始資料問題處理完畢後
需要將推文列表依照每則推文切分
再將每則推文切分出：
推文類型，推文作者，推文內容，推文IP，推文時間 五個欄位
'''

# 匯入原始資料
with sqlite3.connect(r'D:\\research\\data.db') as con:
    df = pd.read_sql('SELECT * FROM 合併資料表', con=con).drop_duplicates('文章ID')  
# 順便刪除 1. 文章ID重複項
print('匯入原始資料完成')

#%%
# 處理 2.3.文章標題遺漏和發文時間遺漏
# 2.3.的情況幾乎都會同時發生，所以以發文時間為目標
clean_list1 = df.index[df['發文時間'] == '#N/A'].tolist()   #取得發文時間為#N/A的index
df.drop(clean_list1, inplace=True)
print('刪除遺漏值完成')

#%%
# 4.5.的問題一起處理
# 規則是僅保留由英數字組成的帳號
df.reset_index(drop=True, inplace=True)  # 重新排列index才能使用for迴圈。舊的index“不會”保留在首個colunm
print('重新排列index')

df['作者'] = df['作者'].str.split(' ').str[0]
print('處理作者資料完成')

#%%
# 切分推文列表，將切分後的結果存入新的data中
column_name1 = ['候選人', '關鍵字', '文章ID', '作者', '文章標題', '發文時間', '文章IP', '文章內文', '推文']
resultlist1 = []

for i in tqdm(range(df.shape[0])):
    candidate = df.iloc[i, 0]
    keyword = df.iloc[i, 1]
    post_ID = df.iloc[i, 2]
    author = df.iloc[i, 3]
    post_title = df.iloc[i, 4]
    post_time = df.iloc[i, 5]
    post_IP = df.iloc[i, 6]
    #post_numofcom = df.iloc[i, 7]   #不再保留留言數的資料
    post_comment = df.iloc[i, 8]
    push_list = str(df.iloc[i, 9])
    push_comment = push_list.split('\n') 

    for j in range(len(push_comment)):
        if push_comment[j].startswith('推 '):
            list1 = [candidate, keyword, post_ID, author, post_title,
                     post_time, post_IP, post_comment, push_comment[j]]
            resultlist1.append(list1)
        elif push_comment[j].startswith('噓 '):
            list2 = [candidate, keyword, post_ID, author, post_title,
                     post_time, post_IP, post_comment, push_comment[j]]
            resultlist1.append(list2)
        elif push_comment[j].startswith('→ '):
            list3 = [candidate, keyword, post_ID, author, post_title,
                     post_time, post_IP, post_comment, push_comment[j]]
            resultlist1.append(list3)

data = pd.DataFrame(resultlist1)
data.columns = column_name1
print('切分推文列表完成')

#%%
# 根據測試，推文中有部分內容查無":"字元，這些推文會導致程式出錯，故先刪除
clean_list2 = data.index[~ data['推文'].str.contains(':')].tolist()
data.drop(clean_list2, inplace=True)
data.reset_index(drop=True, inplace=True)

#%%
# 切分每則貼文，將結果存入data_plus中
# 最後將data_plus合併到data中
column_name2 = ['推文類型', '推文作者', '推文內文', '推文IP', '推文時間']
resultlist2 = []

for p in tqdm(range(data.shape[0])):
    string1 = data.iloc[p, 8]
    string_cut1 = re.split(' ', string1, 1)
    string_cut2 = re.split(':', string_cut1[1], 1)

    # 推文類型
    push_type = string1[0]

    # 推文作者
    push_author = re.split("[^a-zA-Z0-9]+", string_cut1[1], 1)[0]

    # 推文內文
    if push_author != "":
        push_comment = re.sub(
            "(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])|(\d{2})/(\d{2})|(\d{2}):(\d{2})", "", string_cut2[1]).lstrip()
    else:
        push_comment = re.sub(
            "(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])|(\d{2})/(\d{2})|(\d{2}):(\d{2})", "", string_cut1[1]).lstrip()
    # 取出內文的方式是將原字串中,類似IP,日期時間的字串取代成""(意思就是刪除)

    # 推文IP
    if re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', string_cut1[1]) != None:
        push_IP = re.search(
            r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', string_cut1[1]).group()
    else:
        push_IP = ""

    # 推文時間
    if re.search(r"(\d{2}):(\d{2})", string_cut1[1]) != None:
        time = re.search(r"(\d{2}):(\d{2})", string_cut1[1]).group()
    else:
        time = ""

    if re.search(r"(\d{2})/(\d{2})", string_cut1[1]) != None:
        date = re.search(r"(\d{2})/(\d{2})", string_cut1[1]).group()
    else:
        date = ""

    if date != "":
        push_time = str('2018/' + date + ' ' + time)
    else:
        push_time = str('2018/xx/xx' + ' ' + time)
    
    result = [push_type, push_author, push_comment, push_IP, push_time]
    resultlist2.append(result)

data_plus = pd.DataFrame(resultlist2)
data_plus.columns = column_name2
data = pd.concat([data, data_plus], axis=1) #axis=1是橫向合併，axis=0是縱向，預設是axis=0
del data['推文']
print('切分推文內容完成')

#%%
# 匯出到資料庫
print('開始匯出到資料庫，請稍後')
conn = sqlite3.connect(r'E:\\研究專案\\data.db')
c = conn.cursor()
sql = 'INSERT INTO 合併資料表(候選人,關鍵字,文章ID,作者,文章標題,發文時間,文章IP,文章內文,推文類型,推文作者,推文內文,推文IP,推文時間) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
c.executemany(sql, data.to_records(index=False))
conn.commit()
conn.close()
print('匯出資料完成')
