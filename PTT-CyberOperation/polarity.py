# %%
from tqdm import tqdm
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

data_path = r'E:\\research\\data\\候選人資料\\活躍百分位數0.9_留言下限10則_文章不限單一候選人.xlsx'
df = pd.read_excel(data_path, sheet_name='Sheet1')


# %%
polarity = df.groupby(['Region','com_User', 'party'], as_index=False)[['Polarity']].sum()

polarity['KMT'] = np.nan
polarity['DPP'] = np.nan
polarity['OTHER'] = np.nan


def fill_pol2par():
    for i in tqdm(range(len(polarity['com_User']))):
        if polarity.iloc[i, 2] == 'KMT':
            polarity.iloc[i, 4] = polarity.iloc[i, 3]
        elif polarity.iloc[i, 2] == 'DPP':
            polarity.iloc[i, 5] = polarity.iloc[i, 3]
        elif polarity.iloc[i, 2] == 'OTHER':
            polarity.iloc[i, 6] = polarity.iloc[i, 3]


fill_pol2par()

polarity = polarity.groupby(['Region','com_User'], as_index=False)[
    ['KMT', 'DPP', 'OTHER']].sum()

polarity['sum'] = (polarity['KMT'] + polarity['DPP'] + polarity['OTHER'])

# %%
polarity['prefer'] = np.nan
polarity['prefer_value'] = np.nan

def oversum():
    for i in tqdm(range(len(polarity['com_User']))):
        if polarity.iloc[i, 2] > polarity.iloc[i, 5]:
            polarity.iloc[i, 6] = 'KMT'
            polarity.iloc[i, 7] = polarity.iloc[i, 2] - polarity.iloc[i, 5]
        elif polarity.iloc[i, 3] > polarity.iloc[i, 5]:
            polarity.iloc[i, 6] = 'DPP'
            polarity.iloc[i, 7] = polarity.iloc[i, 3] - polarity.iloc[i, 5]
        elif polarity.iloc[i, 4] > polarity.iloc[i, 5]:
            polarity.iloc[i, 6] = 'OTHER'
            polarity.iloc[i, 7] = polarity.iloc[i, 4] - polarity.iloc[i, 5]
        else:
            polarity.iloc[i, 6] = np.nan

oversum()

# %%
