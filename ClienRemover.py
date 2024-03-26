# -*- coding: utf-8 -*-
import codecs
import os
import requests
import time
import threading
from bs4 import BeautifulSoup as bs
from tkinter import *
import sys

# if false, only remove contents on https://www.clien.net/service/board/cm_test
is_release_mode = True

main_url = 'https://www.clien.net'
login_url = 'https://www.clien.net/service/login'
article_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=articles&po='
comment_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=comments&po='
like_article_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=likeArticles&po='
like_comment_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=likeComments&po='

api = 'https://www.clien.net/service/api'

tk = Tk()
removeArticlesLikes = IntVar()
removeCommentsLikes = IntVar()
removeArticles = IntVar()
removeComments = IntVar()

ifProgramRun = True
timeMargin = 4


clienSession = requests.Session()


user_info = {
    'userId' : 'admin',
    'userPassword' : 'user?'
}


def check_end(page):
    soup = bs(page.text, 'html.parser')
    title = soup.select('div.list_myArticle > div > div')
    #print(title)
    try:
        message = title[0].text.strip()
        return True

    except:
        return False


def set_csrf(page, param):
    html = page.text
    soup = bs(html, 'html.parser')
    csrf = soup.find('input', {'name': '_csrf'})
    return {**param, **{'_csrf': csrf['value']}}


def login(user, ID, PW, session):

    user['userId'] = ID
    user['userPassword'] = PW
    user['deviceId'] = ''
    user['totpcode'] = ''

    main_page = session.get(main_url)
    user = set_csrf(main_page, user_info)
    login_req = session.post(login_url, data = user)
    main_page = session.get(main_url)

    soup = bs(main_page.text, 'html.parser')

    soup2 = str(soup.select('div.side_account')[0])

    if "loginForm" in soup2:
        loginState = False
        loginButton['text'] = "로그인 실패"
        loginButton['fg'] = 'red'
    else :
        loginState = True
        loginButton['text'] = "안녕하세요 " + ID + "님"
        loginButton['bg'] = 'greenyellow'
        loginButton['fg'] = 'black'
        loginButton['state'] = 'disabled'
        removeButton['state'] = 'normal'


def removeContents():
    removeButton.config(state = 'disabled')

    #remove comment like
    if removeCommentsLikes.get():
        list_no = 0;
        messageLabel.config(text = "댓글 공감을 철회중입니다.")

        while True:
            if not ifProgramRun:
                sys.exit()
            list_url = like_comment_list_url + str(list_no)
            list_no +=1

            time.sleep(timeMargin)
            list_page = clienSession.get(list_url)
            time.sleep(timeMargin)
            if not check_end(list_page):
                break

            soup = bs(list_page.text, 'html.parser')
            link = soup.select('div.list_title > a.list_subject')

            for l in link:
                comment_info = l.get('href')
                comment_info_sn = comment_info.split('#')[-1]
                comment_info_board = comment_info.split('?c')[0].replace('/service', '')
                commentLikeDeleteApi = api + comment_info_board + '/'+ comment_info_sn
                commentLikeDeleteApi = commentLikeDeleteApi.replace('board', 'comment/like')
                
                #원 게시글이 삭제된 댓글 처리
                if commentLikeDeleteApi == 'https://www.clien.net/service/api#/':
                    onclick = l.get('onclick').replace("'", '').replace('app.cancleLikeComment(', '').replace(');', '')
                    board, board_sn, comment_sn = onclick.split(',')
                    commentLikeDeleteApi = api + '/comment/like/' + board + '/' + board_sn + '/' + comment_sn
                #print(commentLikeDeleteApi)
                
                if is_release_mode or 'cm_test' in commentLikeDeleteApi:
                    try:
                        time.sleep(timeMargin)
                        remove_req = clienSession.post(commentLikeDeleteApi, data = set_csrf(list_page, {}))
                    except:
                        print(commentLikeDeleteApi + " failed")
                

    #remove article like
    if removeArticlesLikes.get():
        list_no = 0
        messageLabel.config(text = "게시글 공감을 철회중입니다.")
        
        while True:
            if not ifProgramRun:
                sys.exit()
            list_url = like_article_list_url + str(list_no)
            list_no += 0

            time.sleep(timeMargin)
            list_page = clienSession.get(list_url)
            if not check_end(list_page):
                break
            soup = bs(list_page.text, 'html.parser')
            link = soup.select('div.list_title > a.list_subject')

            for l in link:
                articleLikeDeleteApi = api + l.get('href').replace('service/board', 'board/like') + '/delete'
                #print(articleLikeDeleteApi)
                
                if is_release_mode or 'cm_test' in articleLikeDeleteApi:
                    try:
                        time.sleep(timeMargin)
                        remove_req = clienSession.post(articleLikeDeleteApi, data = set_csrf(list_page, {}))
                    except:
                        print(articleLikeDeleteApi + " failed")
                
                

    #remove comment
    if removeComments.get():
        list_no = 0;
        messageLabel.config(text = "작성한 댓글이 위치한 게시글 목록을 불러오는 중입니다.")

        while True:
            if not ifProgramRun:
                sys.exit()
            list_url = comment_list_url + str(list_no)
            list_no +=1

            time.sleep(timeMargin)
            list_page = clienSession.get(list_url)
            time.sleep(timeMargin)
            if not check_end(list_page):
                break

            soup = bs(list_page.text, 'html.parser')
            link = soup.select('div.list_title > a.list_subject')

            for l in link:
                comment_info = l.get('href')
                comment_info_sn = comment_info.split('#')[-1]
                comment_info_board = comment_info.split('?c')[0].replace('/service', '')
                commentDeleteAPI = api + comment_info_board + '/comment/delete/'+ comment_info_sn

                #원 게시글이 삭제된 댓글 처리
                if commentDeleteAPI == 'https://www.clien.net/service/api#/comment/delete/':
                    onclick = l.get('onclick').replace("'", '').replace('app.delComment(', '').replace(');', '')
                    board, board_sn, comment_sn = onclick.split(',')
                    commentDeleteAPI = api + '/board/' + board + '/' + board_sn + '/comment/delete/' + comment_sn
                #print(commentDeleteAPI)
                
                if is_release_mode or 'cm_test' in commentDeleteAPI:
                    try:
                        removeReq = clienSession.post(commentDeleteAPI, data = set_csrf(list_page, {}))
                        time.sleep(timeMargin)
                    except:
                        print(commentDeleteAPI, 'failed')
                    


    #remove article
    if removeArticles.get():
        list_no = 0
        messageLabel.config(text = "게시글을 삭제하는 중입니다. 0%")
        time.sleep(timeMargin)
        articleListSizePage = clienSession.get('https://www.clien.net/service/popup/userInfo/basic/' + user_info['userId'])
        articleListSize = int(str(bs(articleListSizePage.text, 'html.parser').select('body > div > div.popup_content > div > div > div:nth-child(1) > div > span.user_article'))[-11:-8])
        print("articleListSize" + str(articleListSize))
        removedArticleListSize = 0

        while True:
            if not ifProgramRun:
                sys.exit()

            
            list_url = article_list_url + str(list_no)
            list_no += 1

            time.sleep(timeMargin)
            list_page = clienSession.get(list_url)
            if not check_end(list_page):
                break

            soup = bs(list_page.text, 'html.parser')
            title = soup.select('div.list_title > a.list_subject')

            for t in title:
                messageLabel.config(text = "게시글을 삭제하는 중입니다." + str(int(removedArticleListSize * 100 / articleListSize)) + "%")

                removedArticleListSize += 1

                articleUrl = main_url + t.get('href')
                articleDeleteApi = api + '/board/' + t.get('href').split('/')[-2] + '/delete'

                time.sleep(timeMargin)
                articlePage = clienSession.get(articleUrl)

                removeArticleData = {
                    'boardSn' : t.get('href').split('/')[-1]
                }

                removeArticleData = set_csrf(articlePage, removeArticleData)
                #print(articleDeleteApi)

                if is_release_mode or 'cm_test' in articleDeleteApi:
                    try:
                        removeReq = clienSession.post(articleDeleteApi, data = removeArticleData)
                        time.sleep(timeMargin)
                    except:
                        print(articleUrl + " failed")
                

    messageLabel.config(text = "요청한 작업을 모두 완성하였습니다.")





tk.title("FineAsh(Clien)")
tk.configure(background='royalblue')
tk.iconbitmap(r''+os.getcwd()+"\clien.ico")


width = 360
height = 270
display_width = tk.winfo_screenwidth()
display_height = tk.winfo_screenwidth()
screen_x = display_width / 2 - width / 2
screen_y = display_height / 4 - height / 2


tk.geometry("%dx%d+%d+%d" % (width, height, screen_x, screen_y))

messageFrame = Frame(tk)
messageFrame.configure(background='deepskyblue')
messageFrame.pack(padx = 20, pady = 20)
messageLabel = Label(messageFrame, text = "FineAsh(CLIEN) 20240327 beta", background='red')
messageLabel.pack()

loginFrame = Frame(tk)
loginFrame.configure(background='deepskyblue')
loginFrame.pack(padx = 10, pady = 10)

loginIDPWFrame = Frame(loginFrame)
loginIDPWFrame.configure(background='deepskyblue')
loginIDPWFrame.pack(padx = 10, pady = 10)

loginIDLabel = Label(loginIDPWFrame, text="아이디", background='deepskyblue')
loginIDLabel.grid(row=1, column=0)
loginIDEntry = Entry(loginIDPWFrame, width=20)
loginIDEntry.grid(row = 1, column = 1)

loginPWLabel = Label(loginIDPWFrame, text = "비밀번호", background='deepskyblue')
loginPWLabel.grid(row = 2, column = 0)
loginPWEntry = Entry(loginIDPWFrame, width=20)
loginPWEntry.grid(row = 2, column = 1)

loginButton = Button(loginFrame, text = "로그인", command= lambda: login(user_info, loginIDEntry.get(), loginPWEntry.get(), clienSession), background='white')
loginButton.pack()

optionFrame = Frame(tk)
optionFrame.configure(background='deepskyblue')
optionFrame.pack(padx = 10, pady = 10);

option1 = Checkbutton(optionFrame, text = "공감글 ", variable = removeArticlesLikes, background = 'deepskyblue')
option2 = Checkbutton(optionFrame, text = "공감댓글", variable = removeCommentsLikes, background = 'deepskyblue')
option3 = Checkbutton(optionFrame, text = "글  ", variable = removeArticles, background = 'deepskyblue')
option4 = Checkbutton(optionFrame, text = "댓글", variable = removeComments, background = 'deepskyblue')

#option1.select()
#option2.select()
#option3.select()
#option4.select()

option1.grid(row = 0, column = 0)
option2.grid(row = 0, column = 1)
option3.grid(row = 0, column = 2)
option4.grid(row = 0, column = 3)

removeContentsThread = threading.Thread(target=removeContents)
removeButton = Button(tk, text = "삭제", state = 'disabled', command = lambda: removeContentsThread.start())
removeButton.pack()

tk.mainloop()


ifProgramRun = False
