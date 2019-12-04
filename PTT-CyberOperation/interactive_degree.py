# %%
# 匯入函式庫以及資料
import sqlite3
import pandas as pd

with sqlite3.connect(r'E:\\research\\data\\data.db') as con:
    df = pd.read_sql('SELECT * FROM 推文帳號互動概況', con=con)

# print(df.head())
# print(df.info())

# 篩選總留言數在10(含)以上的資料
# 因為留言數太少會使互動的機率變得較為極端

data = df[df['總留言數'] > 10]

data.drop(data[data['推文作者'] == ''].index.tolist(), inplace=True)
data.reset_index(drop=True, inplace=True)

# 修改一下名稱,因為之前的名稱不太好辨認
data.rename(columns={
            '作者': '文章作者', '在此作者下的留言機率': '所有留言中留言作者的機率',
             '留言帳號推作者的機率': '所有留言中推作者的機率', '留言帳號噓作者的機率': '所有留言中噓作者的機率'}
             , inplace=True)

# %%
# 計算在此作者下的推文/總推文數

data['所有推文中推作者的機率'] = data['在此作者下的推文數'] / data['總推文數']
data['所有噓文中噓作者的機率'] = data['在此作者下的噓文數'] / data['總噓文數']

# 重新排列欄
col = ['推文作者', '文章作者', '總留言數', '總推文數', '總噓文數',
       '在此作者下的留言數', '在此作者下的推文數', '在此作者下的噓文數',
       '所有留言中留言作者的機率', '所有推文中推作者的機率', '所有噓文中噓作者的機率',
        '所有留言中推作者的機率', '所有留言中噓作者的機率']

data = data.reindex(columns=col)

# %%
# 留言機率在50%，60%，70%，80%，90%以上的資料
# 以5個級距代表互動程度低到高

list50_90 = list(range(50, 100, 10))  # 返回[50,60,70,80,90]

for i in list50_90:
    locals()['com%s' % i] = data[data['所有留言中留言作者的機率'] >= i/100]  # 用動態方式建立變數

sheetsname = '留言機率'

# 以Excel的方式保存到檔案夾中

with pd.ExcelWriter(r'E:\\research\\data\\留言機率50_90.xlsx') as writer:
    for i in list50_90:
        locals()['com%s' % i].to_excel(writer, sheetsname+str(i), index=False)


# %%
