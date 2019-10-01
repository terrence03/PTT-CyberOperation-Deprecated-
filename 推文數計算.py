# %%
import sqlite3
import pandas as pd
from tqdm import tqdm

# 讀入資料
with sqlite3.connect(r'E:\\research\\資料\\data.db') as con:
    data = pd.read_sql_query(
        "SELECT 文章ID,候選人,作者,文章IP,發文時間,推文類型,推文作者,推文內文,推文IP,推文時間 FROM 合併資料表", con=con)

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

# %%
# 計算留言帳號在每個作者下留言的機率
count_comment = data.groupby(['推文作者', '作者'], as_index=False)[
    '推文內文'].agg({'在此作者下的留言數': 'count'})

sum_comment = count_comment.groupby(['推文作者'], as_index=False)[
    '在此作者下的留言數'].agg({'總留言數': 'sum'})

cross_comment = pd.merge(count_comment, sum_comment)
cross_comment['在此作者下的留言機率'] = cross_comment['在此作者下的留言數']/cross_comment['總留言數']


# %%
# 計算推文帳號在每個作者下推文的機率
data_upvote = data[data['推文類型'] == '推']

count_upvote = data_upvote.groupby(['推文作者', '作者'], as_index=False)[
    '推文類型'].agg({'在此作者下的推文數': 'count'})

sum_upvote = count_upvote.groupby(['推文作者'], as_index=False)[
    '在此作者下的推文數'].agg({'總推文數': 'sum'})

cross_upvote = pd.merge(count_upvote, sum_upvote)
cross_upvote['推文機率'] = cross_upvote['在此作者下的推文數']/cross_upvote['總推文數']

# %%
# 計算推文帳號在每個作者下推文的機率
data_dnvote = data[data['推文類型'] == '噓']

count_dnvote = data_dnvote.groupby(['推文作者', '作者'], as_index=False)[
    '推文類型'].agg({'在此作者下的噓文數': 'count'})

sum_dnvote = count_dnvote.groupby(['推文作者'], as_index=False)[
    '在此作者下的噓文數'].agg({'總噓文數': 'sum'})

cross_dnvote = pd.merge(count_dnvote, sum_dnvote)
cross_dnvote['噓文機率'] = cross_dnvote['在此作者下的噓文數']/cross_dnvote['總噓文數']


# %%
# 計算留言者的推文率，噓文率，箭頭率
total_comment = data.groupby(['推文作者'], as_index=False)['推文內文'].agg(
    {'總留言數': 'count'})  # 用來計算每個留言帳號在整個資料中的留言數量
total_upvote = data_upvote.groupby(['推文作者'], as_index=False)[
    '推文內文'].agg({'總推文數': 'count'})
total_dnvote = data_dnvote.groupby(['推文作者'], as_index=False)[
    '推文內文'].agg({'總噓文數': 'count'})

total_info = pd.merge(pd.merge(total_comment, total_upvote,
                               how='left'), total_dnvote, how='left')
total_info.fillna(0, inplace=True)
total_info['總箭頭數'] = total_info['總留言數']-total_info['總推文數']-total_info['總噓文數']
total_info['推文率'] = total_info['總推文數']/total_info['總留言數']
total_info['噓文率'] = total_info['總噓文數']/total_info['總留言數']
total_info['箭頭率'] = total_info['總箭頭數']/total_info['總留言數']

total_info['總推文數'] = total_info['總推文數'].astype('int64')
total_info['總噓文數'] = total_info['總噓文數'].astype('int64')
total_info['總箭頭數'] = total_info['總箭頭數'].astype('int64')

# %%
# 擴展cross_comment，加入計算再所有互動中對特定作者的推文、噓文和箭頭


def get_All():
    a = pd.merge(cross_comment, count_upvote, on=['推文作者', '作者'], how='left')
    b = pd.merge(a, sum_upvote, on='推文作者', how='left')
    b = b.fillna(0)
    b['留言帳號推作者的機率'] = b['在此作者下的推文數']/b['總留言數']
    c = pd.merge(b, count_dnvote, on=['推文作者', '作者'], how='left')
    d = pd.merge(c, sum_dnvote, on='推文作者', how='left')
    d = d.fillna(0)
    d['留言帳號噓作者的機率'] = d['在此作者下的噓文數']/d['總留言數']
    d['在此作者下的推文數'] = d['在此作者下的推文數'].astype('int64')
    d['總推文數'] = d['總推文數'].astype('int64')
    d['在此作者下的噓文數'] = d['在此作者下的噓文數'].astype('int64')
    d['總噓文數'] = d['總噓文數'].astype('int64')
    return d


# %%
# 輸出結果
with sqlite3.connect(r'E:\\research\\資料\\data.db') as con:
    get_All().to_sql(name='推文帳號面貌', con=con, if_exists='append', index=False)


#%%
