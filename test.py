import re

#string = "柯文哲|推 就照標準來啊 又不是不坐捷運就會死   61.230.127.219 07/16 11:11|1RJ2t4UK"
#string = "丁守中|推 arext:不過我碩二了..不知道還有沒有需要補充的|1RAwUUZY"
string = "柯文哲|→ 所以說柯文哲嘴前瞻真惡劣，沒票的地方就亂嘴   61.230.127.219 07/16 11:11|1RJ2t4UK"

step1 = string.split("|")
step2 = re.split(" ", step1[1], 1)
step3 = re.split("[^a-zA-Z0-9]+",step2[1], 1)

push_type = step2[0]
push_author = step3[0]

if re.search(r"(\d{2}):(\d{2})", step2[1]) != None:
    time = re.search(r"(\d{2}):(\d{2})", step2[1]).group()
else:
    time = ""
if re.search(r"(\d{2})/(\d{2})", step2[1]) != None:
    date = re.search(r"(\d{2})/(\d{2})", step2[1]).group()
else:
<<<<<<< HEAD
    print("no")

string = "柯文哲|→ kc: 所以說柯文哲嘴前瞻真惡劣，沒票的地方就亂嘴   61.230.127.219 07/16 13:42|1RJ2t4UK"
#re.findall(r"(\d{2}):(\d{2})", string)y = re.findall(r"(\d{2}):(\d{2})", string)
if re.findall(r"(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])", string) != []:
    print("yes")
else:
    print("no")
"""

string = "所以說柯文哲嘴前瞻真惡劣，沒票的地方就亂嘴   61.230.127.219 07/16 13:42"

if re.search(r"(\d{2}):(\d{2})", string) != []:
    time = re.search(r"(\d{2}):(\d{2})", string).group()
else:
    time = ""
            
if re.search(r"(\d{2})/(\d{2})", string) != [] :
    date = re.search(r"(\d{2})/(\d{2})", string).group()
else:
    date = ""
           
if re.search(r"(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])", string) != [] :
    ip = re.search(r"(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])", string).group()
else:
    ip = ""

"""
if len(string) >= 27:
    push_comment = string[0:23]
elif len(string) >=
#string = "５毛  嘘"
#push_comment = string[0:-27]
"""
print(time, date, ip)
=======
    date = ""
if re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', step2[1]) != None:
    ip = re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', step2[1]).group()
else:
    ip = ""

push_comment = re.sub(
    "(^[a-zA-Z0-9]+:)|(\d{2}:\d{2})|(\d{2}/\d{2})|(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])", "", step2[1]).lstrip()


#測試結果
print(" 作者：", push_author, "\n","類型：", push_type,"\n","內文：",
    push_comment,"\n","時間：",time,"\n","日期：",date,"\n","IP  ：",ip)

>>>>>>> 2f8c54759aea7f1e1dd9a77879d94b2451a7497d
