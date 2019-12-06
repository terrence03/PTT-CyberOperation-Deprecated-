# %%
from opencc import OpenCC
import sqlite3
import pandas as pd

# %%
with sqlite3.connect(r'E:\\research\\data\\sql\\data.db') as con:
    df = pd.read_sql('SELECT 推文內文 FROM 推文資料', con=con)

# %%
from tqdm import tqdm
with open('result.txt', 'a', encoding='utf-8') as result:
    for i in tqdm(range(0,2882410,30)):
        result.write(str(df.iloc[i, 0]).strip() + '\n')

# %%
cc = OpenCC('t2s')
source = open('test.txt', 'r', encoding='utf-8')
result = open('test_translated.txt', 'w', encoding='utf-8')
#source就放純文字檔，轉完就放進去result
count = 0
while True:
    line = source.readline()
    line = cc.convert(line)
    if not line:  # readline會一直讀下去，這邊做的break
        break
    #print(line)
    count = count + 1
    result.write(line)
    #print('===已處理'+str(count)+'行===')
source.close()
result.close()


# %%
