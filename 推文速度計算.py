import pandas as pd

#讀取csv資料
csvfile = pd.read_csv("推文.csv")
#print(csvflie["文章ID"][5])

group = csvfile.groupby("文章ID")
csvfile["推文時間"] = pd.to_datetime(csvfile["推文時間"])

print(group.sum())
#column = len(csvflie["文章ID"])

"""
for i in range(int(column)):
    upvote = csvflie["推文類型"][i] == "推"
    neutral = csvflie["推文類型"][i] == "→"
    downvote = csvflie["推文類型"][i] == "噓"
    if csvflie["文章ID"][i] == csvflie["文章ID"][i+1]:
        print(csvflie["文章ID"][i])
"""