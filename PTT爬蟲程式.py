import sys
import time
import json
import getpass
import codecs
import traceback
from PTTLibrary import PTT
from uao import Big5UAOCodec
import sqlite3

uao = Big5UAOCodec()

BoardList = ['Gossiping']

PTTBot = None
ResPath = './OldBug/'

def PostHandler(Post):
    #這是 crawlBoard 需要的 call back function
    #每當爬蟲取得新文章就會呼叫此函式一次
    #因此你可以在這自由地決定存檔的格式 或者任何你想做的分析

    #文章資料結構可參考如下
    ################## 文章資訊 Post information ##################
    # getBoard                  文章所在版面
    # getID                     文章 ID ex: 1PCBfel1
    # getAuthor                 作者
    # getDate                   文章發布時間
    # getTitle                  文章標題
    # getContent                文章內文
    # getMoney                  文章P幣
    # getWebUrl                 文章網址
    # getPushList               文章即時推文清單
    # ListDate                  文章列表的日期
    # getOriginalData           文章原始資料 (備份用)

    ################## 推文資訊 Push information ##################
    # getType                   推文類別 推噓箭頭
    # getAuthor                 推文ID
    # getContent                推文內文
    # getIP                     推文IP
    # getTime                   推文時間

    #原版（PTTLibrary）的程式中，是將爬蟲結果存入文字檔
    #為了之後方便處理，和原版不同的是，這裡將結果存入sqlite中

    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    #在PTTLibrary 0.8.0 版本以前，推文資訊是包含在文章內文當中，沒有切分出來，所以此處先將推文列表切出
    #此處是切分後的文章內文
    content = Post.getContent()
    content = content[content.find('───────────────────────────────────────') + len('───────────────────────────────────────'):]
    content = content[:content.find('※ 發信站: 批踢踢實業坊(ptt.cc)')]
    
    #此處是切分後的推文列表
    pushlist = Post.getContent()
    pushlist = pushlist[pushlist.find('※ 文章網址: ') + len('※ 文章網址: '):]

    result_value = list([
        str("韓國瑜"), str("韓"),str(Post.getID()),str(Post.getAuthor()),
        str(Post.getTitle()),str(Post.getDate()),str(Post.getIP()),
        len(Post.getPushList()),str(content),str(pushlist)
        ])
    c.execute("INSERT INTO 韓國瑜 (候選人,關鍵字,文章ID,作者,文章標題,發文時間,文章IP,留言數,文章內文,推文列表) VALUES (?,?,?,?,?,?,?,?,?,?)", result_value)
    conn.commit()
    conn.close()
    #time.sleep(0.5)    #限制爬蟲速度，避免造成系統負擔

def CrawlBoard():
    ################## 文章搜尋資訊 Post Search Type information ###
    # Unknow                    不搜尋 無作用
    # Keyword                   搜尋關鍵字
    # Author                    搜尋作者
    # Push                      搜尋推文數
    # Mark                      搜尋標記 m or s
    # Money                     搜尋稿酬
    # ex: PTT.PostSearchType.Keyword

    EnableSearchCondition = True
    inputSearchType = PTT.PostSearchType.Keyword
    inputSearch = '韓'

    if EnableSearchCondition:
        ErrCode, NewestIndex = PTTBot.getNewestIndex(Board = 'Gossiping', SearchType = inputSearchType, Search = inputSearch)
    else:
        ErrCode, NewestIndex = PTTBot.getNewestIndex(Board = 'Gossiping')

    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('取得 ' + 'Gossiping' + '板最新文章編號成功' + str(NewestIndex))
    else:
        PTTBot.Log('取得 ' + 'Gossiping' + '板最新文章編號失敗')
        return False
    
    if EnableSearchCondition:
        ErrCode, SuccessCount, DeleteCount = PTTBot.crawlBoard('Gossiping', PostHandler, StartIndex= 9459 , EndIndex= 9500 , SearchType=inputSearchType, Search=inputSearch)
        #上列的StartIndex= 1 , EndIndex= 9500 和原版不一樣的原因是，我希望從最早的文章開始爬，並設定截止值，方便爬蟲中斷時調整，不用從頭開始
    else:
        ErrCode, SuccessCount, DeleteCount = PTTBot.crawlBoard('Gossiping', PostHandler, StartIndex= 9459 , EndIndex= 9500 )

    if ErrCode == PTT.ErrorCode.Success:
        PTTBot.Log('爬行成功共 ' + str(SuccessCount) + ' 篇文章 共有 ' + str(DeleteCount) + ' 篇文章被刪除')


#使用Account.txt來讀入帳號密碼
try:
    with open('Account.txt') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
except FileNotFoundError:
    ID = input('請輸入帳號: ')
    Password = getpass.getpass('請輸入密碼: ')

#是否要在登入時踢掉其他登入？
PTTBot = PTT.Library(kickOtherLogin=True)
#登入
ErrCode = PTTBot.login(ID, Password)
#使用錯誤碼，判斷登入是否成功
if ErrCode != PTT.ErrorCode.Success:
    PTTBot.Log('登入失敗')
    sys.exit()

try:
     CrawlBoard() 
     pass
except Exception as e:
        
    traceback.print_tb(e.__traceback__)
    print(e)
    PTTBot.Log('接到例外 啟動緊急應變措施')

#登出
PTTBot.logout()
