import re
"""
if "柯文哲|→ kc: 所以說柯文哲嘴前瞻真惡劣，沒票的地方就亂嘴   61.230.127.219 07/16 13:42|1RJ2t4UK".find("[00-24]:[00-60]") == -1:
    print("yes")
else:
    print("no")
"""

string = "柯文哲|→ kc: 所以說柯文哲嘴前瞻真惡劣，沒票的地方就亂嘴   61.230.127.219 07/16 13:42|1RJ2t4UK"
y = re.findall(r"[00-99]", string)
print(y)