import re
"""
if "柯文哲|→ kc: 所以說柯文哲嘴前瞻真惡劣，沒票的地方就亂嘴   61.230.127.219 07/16 13:42|1RJ2t4UK".find("[00-24]:[00-60]") == -1:
    print("yes")
else:
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