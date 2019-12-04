# %%
# 匯入套件
import seaborn as sns
from matplotlib import pyplot as plt
import sqlite3
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import re
import numpy as np

CyberArmy90 = pd.read_excel(
    r'E:\\research\\data\\候選人資料\\活躍百分位數0.9_留言下限10則_文章不限單一候選人.xlsx')

CyberArmy90_tpe = CyberArmy90[CyberArmy90['Region'] == '臺北市']

# %%
trans_data_Ko = CyberArmy90_tpe[CyberArmy90_tpe['Candidate'] == '柯文哲'][[
    'com_Content', 'Polarity']]
trans_data_Yao = CyberArmy90_tpe[CyberArmy90_tpe['Candidate'] == '姚文智'][[
    'com_Content', 'Polarity']]
trans_data_Ting = CyberArmy90_tpe[CyberArmy90_tpe['Candidate'] == '丁守中'][[
    'com_Content', 'Polarity']]

fig = plt.figure(figsize=(16,10), dpi=300)
#grid = plt.GridSpec(2, 2, wspace=0.4, hspace=0.3)

#plt.subplot(grid[0, 0])
plt.subplot(2,2,1)
x = trans_data_Ko['com_Content']
y = trans_data_Ko['Polarity']
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
#sns.regplot('com_Content', 'Polarity', trans_data_Ko, color='r',)
plt.plot(x, p(x), 'r--')
plt.scatter(x, y, alpha=0.6, c='gray')
plt.title('Ko')

#plt.subplot(grid[0, 1])
plt.subplot(2,2,2)
x = trans_data_Yao['com_Content']
y = trans_data_Yao['Polarity']
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
#sns.regplot('com_Content', 'Polarity', trans_data_Yao, color='r',)
plt.plot(x, p(x), 'r--')
plt.scatter(x, y, alpha=0.6, c='green')
plt.title('Yao')

#plt.subplot(grid[1, 1])
plt.subplot(2,2,3)
x = trans_data_Ting['com_Content']
y = trans_data_Ting['Polarity']
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
#sns.regplot('com_Content', 'Polarity', trans_data_Ting, color='r',)
plt.plot(x, p(x), 'r--')
plt.scatter(x, y, alpha=0.6, c='blue')
plt.title('Ting')

plt.savefig(r'E:\\research\\data\\圖庫\\tpe.png')
plt.show()



# %%
