import csv
import codecs
import sqlite3
import re
from tqdm import tqdm

"""
此程式將每則推文的資訊切分出：
推文類型，推文作者，推文內容，推文IP，推文日期，推文時間
並將資料存入sqlite中
"""

#candidate_list = ["一般縣市候選人", "丁守中", "侯友宜", "其他直轄市候選人", "姚文智", "林佳龍", "柯文哲", "盧秀燕", "蘇貞昌", "鄭文燦", "陳其邁", "陳學聖", "韓國瑜", "高思博", "黃偉哲"]

def main():

    with open(r'D:\\research\\資料\\推文資料\\推文資料_侯友宜.csv', 'r', encoding="utf-8") as csvFile:
    
        rows = list(csv.reader(csvFile))


        conn = sqlite3.connect(r'D:\\research\\data.db')
        print("Open database successfully")

        c = conn.cursor()

        for row in tqdm(rows):
            string = str(row)
            step1 = string.split("|")
            step2 = step1[1].split(":",1)
            step3 = step2[0].split(" ", 1)

            candidate = step1[0].replace("['", '')
            
            postID = step1[2].replace("']", '')
            
            push_type = step3[0]
            
            push_author = step3[1]
            
            # 此處使用時間的正規表示法(\d{2}):(\d{2})
            if re.search(r"(\d{2}):(\d{2})", step2[1]) != None:
                time = re.search(r"(\d{2}):(\d{2})", step2[1]).group()
            else:
                time = ""
            
            # 此處使用日期的正規表示法(\d{2})/(\d{2})
            if re.search(r"(\d{2})/(\d{2})", step2[1]) != None:
                date = re.search(r"(\d{2})/(\d{2})", step2[1]).group()
            else:
                date = ""
           
            # 此處使用IP的正規表示法(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])
            if re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', step2[1]) != None:
                ip = re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', step2[1]).group()
            else:
                ip = ""

            push_comment = re.sub(
                "(\d{2}:\d{2})|(\d{2}/\d{2})|(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])", "", step2[1]).lstrip()  # 用re.sub取代時可以用|號來進行多個取代

            #print(candidate, postID)

            #將結果存入sqlite
            #包含IP資訊
            result_value = [postID, candidate, push_type, push_author, push_comment, ip, date, time]

            c.execute("INSERT INTO 推文資料 (文章ID,候選人,推文類型,推文作者,推文內文,推文IP,推文日期,推文時間) VALUES (?,?,?,?,?,?,?,?)", result_value)
            
            conn.commit()
            
            #不含ip
            #with open("推文資料_一般縣市候選人_切分結果(無ip).csv", "a", encoding = "utf-8") as ResultFile:
                #ResultFile.write(candidate + "|" + push_type + "|" + push_author + "|" + push_comment + "|" + date + "|" + time + "|" + postID + "\n" )
            
            #包含ip
            #with open("推文資料_一般縣市候選人_切分結果.csv", "a", encoding = "utf-8") as ResultFile:
            #    ResultFile.write(candidate + "|" + push_type + "|" + push_author + "|" + push_comment + "|" + ip + "|" + date + "|" + time + "|" + postID + "\n" )
        
        conn.close()
        print("finish")


if __name__ == "__main__":
    main()
