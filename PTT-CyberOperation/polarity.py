# %%
from tqdm import tqdm
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

data_path = r'E:\\research\\data\\候選人資料\\活躍百分位數0.9_留言下限10則_文章不限單一候選人.xlsx'
df = pd.read_excel(data_path, sheet_name='Sheet1')
polarity = df.groupby(['com_User', 'Region', 'party'],
                      as_index=False)[['Polarity']].sum()

# %%
polarity["KMT"] = np.nan
polarity["DPP"] = np.nan
polarity["OTHER"] = np.nan


def fill_pol2par():
    for i in tqdm(range(len(polarity["com_User"]))):
        if polarity.iloc[i, 2] == "KMT":
            polarity.iloc[i, 4] = polarity.iloc[i, 3]
        elif polarity.iloc[i, 2] == "DPP":
            polarity.iloc[i, 5] = polarity.iloc[i, 3]
        elif polarity.iloc[i, 2] == "OTHER":
            polarity.iloc[i, 6] = polarity.iloc[i, 3]


fill_pol2par()

polarity = polarity.groupby(['Region', 'com_User'], as_index=False)[
    ['KMT', 'DPP', 'OTHER']].sum()

polarity["sum"] = polarity["KMT"] + polarity["DPP"] + polarity["OTHER"]

# %%
polarity["prefer"] = np.nan
polarity["prefer_value"] = np.nan



def oversum():
    for i in tqdm(range(len(polarity["com_User"]))):
        if polarity.iloc[i, 2] > polarity.iloc[i, 5]:
            polarity.iloc[i, 6] = "KMT"
            polarity.iloc[i, 7] = polarity.iloc[i, 2] - polarity.iloc[i, 5]
        elif polarity.iloc[i, 3] > polarity.iloc[i, 5]:
            polarity.iloc[i, 6] = "DPP"
            polarity.iloc[i, 7] = polarity.iloc[i, 3] - polarity.iloc[i, 5]
        elif polarity.iloc[i, 4] > polarity.iloc[i, 5]:
            polarity.iloc[i, 6] = "OTHER"
            polarity.iloc[i, 7] = polarity.iloc[i, 4] - polarity.iloc[i, 5]
        else:
            polarity.iloc[i, 6] = np.nan


oversum()

# %%


def prefer_party(DateFrame, Criterion, multiple=1):
    if Criterion == 'sum':
        polarity_1 = DateFrame.groupby(['com_User', 'Region'], as_index=False)[
            'Polarity'].sum()
    elif Criterion == 'max':
        polarity_1 = DateFrame.groupby(['com_User', 'Region'], as_index=False)[
            'Polarity'].max()
    elif Criterion == 'sum&max':
        polarity_1 = DateFrame.groupby(['com_User', 'Region'], as_index=False)[
            'Polarity'].agg({'sum': 'sum', 'max': 'max'})
        polarity_1['sum&max'] = np.nan
        for s in range(len(polarity_1['com_User'])):
            polarity_1.iloc[s, 4] = max([polarity_1.iloc[s, 2], polarity_1.iloc[s, 3]])
        del polarity_1['sum']
        del polarity_1['max']

    polarity_1 = pd.merge(DateFrame, polarity_1, 'left',
                          ['com_User', 'Region'])
    polarity_1['perfer_party'] = np.nan
    polarity_1['perfer_value'] = np.nan

    for i in tqdm(range(len(polarity_1['com_User']))):
        if polarity_1.iloc[i, 3] >= polarity_1.iloc[i, 4]*multiple and polarity_1.iloc[i, 3] > 0:
            polarity_1.iloc[i, 5] = polarity_1.iloc[i, 2]
            polarity_1.iloc[i, 6] = polarity_1.iloc[i, 3] - \
                polarity_1.iloc[i, 4]

        else:
            polarity_1.iloc[i, 5] = np.nan

    if Criterion == 'sum':
        polarity_1.columns = ['com_User', 'Region', 'party',
                              'Polarity', 'Polarity_sum', 'prefer_party', 'prefer_value']
    elif Criterion == 'max':
         polarity_1.columns = ['com_User', 'Region', 'party',
                               'Polarity', 'Polarity_max', 'prefer_party', 'prefer_value']
    elif Criterion == 'max':
         polarity_1.columns = ['com_User', 'Region', 'party',
                               'Polarity', 'Polarity_sum&max', 'prefer_party', 'prefer_value']    
    
    print('共有: ' + str(len(set(polarity_1.dropna()['com_User']))) + ' 個用戶')
    return polarity_1.dropna()


# %%
