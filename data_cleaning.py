# %%
# 匯入套件
import sqlite3
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import re
import numpy as np

# %%
'''
以下問題會在程式中處理
1. 文章ID重複
2. 文章標題的資料遺漏（通常情況是該欄位的值是None）
3. 發文時間的資料遺漏（通常情況是該欄位的值是#N/A）
4. 作者的資料常常包含換行、特殊符號
5. 作者的欄位有文章的內文
6. 吳蕚洋的名字在文章標題
7. 發文時間格式的正確性
8. 文章IP格式的正確性
9. 發文時間限定在2018-06-17~2018-11-23
10. 推文列表的欄位有文章的內文

原始資料問題處理完畢後
需要將推文列表依照每則推文切分
再將每則推文切分出：
推文類型，推文作者，推文內容，推文IP，推文時間 五個欄位
'''

# 匯入原始資料
with sqlite3.connect(r'D:\\research\\data\\sql\\data_original.db') as con:
    df = pd.read_sql('SELECT * FROM 合併資料表', con=con).drop_duplicates('文章ID')
# 順便刪除 1. 文章ID重複項
print('匯入原始資料完成')

# %%
# 處理 2.3.文章標題遺漏和發文時間遺漏
# 2.3.的情況幾乎都會同時發生，所以以發文時間為目標
clean_list1 = df.index[df['發文時間'] == '#N/A'].tolist()  # 取得發文時間為#N/A的index
df.drop(clean_list1, inplace=True)
print('刪除文章標題和發文時間遺漏完成')

# %%
# 4.5.的問題一起處理
# 規則是僅保留由英數字組成的帳號
df['作者'] = df['作者'].str.split(' ').str[0]
print('處理作者資料完成')

# %%
# 6.是因為轉碼導致出現亂碼,吳蕚洋名字中會出現空格或換行符號
df['文章標題'] = df['文章標題'].str.replace('\n', '')
df.replace(regex={'吳  蕚': '吳蕚'}, inplace=True)

# %%
# 8.和9.的問題一併處理,將時間套用成datetime的格式
df['datetime'] = df['發文時間'].map(
    lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
del df['發文時間']  # 有格式化的時間後就可以把原本的時間欄刪除了

re_ip = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
df.loc[(df['文章IP'].str.contains(re_ip) == None)]  # 回傳的資料是空的表示全部IP都是符合規範的

# %%
# 10.限定發文時間範圍在2018-06-17~2018-11-23


def get_daterange_data(DataFrame, start_date, end_date):
    '''
        DataFrame: 一個包含'datetime'欄位的DateFrame物件
    '''
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    mask = (DataFrame['datetime'] > start_date) & (
        DataFrame['datetime'] < end_date)

    return DataFrame.loc[mask]


df = get_daterange_data(df, '2018-06-17', '2018-11-23')
# %%
# 文章清洗完成,修改欄位名,存檔
df.columns = ['Candidate', 'Keyword', 'post_ID', 'post_Author', 'post_Title',
              'post_IP', 'n_com', 'post_Content', 'push_List', 'post_Datetime']

with sqlite3.connect(r'D:\\research\\data\\sql\\analysis.db') as con:
    df.to_sql('original_post', con, index=False)

# %%
# 切分推文列表，將切分後的結果存入新的data中,10.問題會在這裡被處理
df.reset_index(drop=True, inplace=True)  # 重新排列index才能使用for迴圈
print('重新排列index')


def split_push():
    column_name = ['post_ID', 'push']

    resultlist = []
    for i in tqdm(range(df.shape[0])):
        post_ID = df.iloc[i, 2]
        push_list = str(df.iloc[i, 8])
        push_comment = push_list.split('\n')

        for j in range(len(push_comment)):
            if push_comment[j].startswith('推 '):
                list1 = [post_ID, push_comment[j]]
                resultlist.append(list1)
            elif push_comment[j].startswith('噓 '):
                list2 = [post_ID, push_comment[j]]
                resultlist.append(list2)
            elif push_comment[j].startswith('→ '):
                list3 = [post_ID, push_comment[j]]
                resultlist.append(list3)

    data = pd.DataFrame(resultlist)
    data.columns = column_name
    print('切分推文列表完成')
    return data


data = split_push()
# %%
# 根據測試，推文中有部分內容查無":"字元，這些推文會導致程式出錯，故先刪除
clean_list2 = data.index[~ data['push'].str.contains(':')].tolist()
data.drop(clean_list2, inplace=True)
data.reset_index(drop=True, inplace=True)

# %%
# 切分每則貼文，將結果存入data_plus中
# 最後將data_plus合併到data中


def classfy_push(DataFrame):
    '''
    data:需要一個包含['post_ID']和['push']所在的DataFrame,如data
    '''
    data = DataFrame['push']
    postID = DataFrame['post_ID']
    column_name = ['post_ID','com_Type', 'com_User', 'com_Content', 'com_IP', 'com_Datetime']
    resultlist = []

    for i in range(len(data)):
        string1 = data[i]
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
            push_IP = np.nan

        # 推文時間
        if re.search(r"(\d{2})/(\d{2}) (\d{2}):(\d{2})", string_cut1[1]) != None:
            datetime = '2018/' + re.search(
                r"(\d{2})/(\d{2}) (\d{2}):(\d{2})", string_cut1[1]).group()
        else:
            datetime = np.nan


        result = [postID[i], push_type, push_author, push_comment, push_IP, datetime]
        resultlist.append(result)
    
    print('切分推文內容完成')
    data_plus = pd.DataFrame(resultlist)
    data_plus.columns = column_name
    
    return data_plus

data_plus = classfy_push(data)
# axis=1是橫向合併，axis=0是縱向，預設是axis=0

# %%
# 將留言切分結果存檔
with sqlite3.connect(r'D:\\research\\data\\sql\\analysis.db') as con:
    data_plus.to_sql('original_push', con, index=False)
