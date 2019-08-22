import sqlite3
import codecs

"""
此程式將PTT爬蟲程式的結果再進一步處理
將推文列表依據每則詳細切分
最後切分出的結果存到csv文字檔中
"""

#讀入資料
conn = sqlite3.connect("data.db")
print("Open database successfully")

#candidate_list = ["一般縣市候選人", "丁守中", "侯友宜", "其他直轄市候選人", "姚文智", "林佳龍", "柯文哲", "盧秀燕", "蘇貞昌", "鄭文燦", "陳其邁", "陳學聖", "韓國瑜", "高思博", "黃偉哲"]

cursor = conn.execute("SELECT * from 黃偉哲")

#切分留言
for j in cursor:
    candidate = j[0]
    postID = j[2]
    com = j[9]
    string = str(com)
    comment = string.split("\n")
    #print(comment)
        
    for i in range(len(comment)):
        if(comment[i].startswith("推 ")):
            with codecs.open("推文資料_黃偉哲.csv", "a", "utf-8") as ResultFile:
                ResultFile.write(candidate + "|" + comment[i] + "|" + postID + "\n")
        elif(comment[i].startswith("噓 ")):
            with codecs.open("推文資料_黃偉哲.csv", "a", "utf-8") as ResultFile:
                ResultFile.write(candidate + "|" + comment[i] + "|" + postID + "\n")
        elif(comment[i].startswith("→ ")):
            with codecs.open("推文資料_黃偉哲.csv", "a", "utf-8") as ResultFile:
                ResultFile.write(candidate + "|" + comment[i] + "|" + postID + "\n")

conn.close()
print("finish")
