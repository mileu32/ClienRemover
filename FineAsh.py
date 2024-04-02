import codecs
import os
import sys
import threading
import time

from tkinter import *
from ClienClient import *


article_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=articles&po='
comment_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=comments&po='
like_article_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=likeArticles&po='
like_comment_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=likeComments&po='


tk = Tk()
removeLikes = IntVar()
removeArticles = IntVar()
removeComments = IntVar()
loginID = StringVar()
loginPW = StringVar()
is_program_run = True


cc = ClienClient(release_mode=True)


def check_end(page):
    soup = bs(page.text, 'html.parser')
    title = soup.select('div.list_myArticle > div > div')
    try:
        message = title[0].text.strip()
        return True
    except:
        return False

def login(ID, PW):
    if cc.login(ID, PW):
        cc.set_info()
        loginButton['text'] = "안녕하세요 " + cc.nickname + "님"
        loginID.set(cc.signin_id)
        loginPW.set(' ' * 8)
        loginButton['state'] = 'disabled'
        removeButton['state'] = 'normal'
    else:
        loginState = False
        loginButton['text'] = "로그인 실패"
        loginButton['fg'] = 'red'



def removeContents():
    removeButton.config(state = 'disabled')

    #remove comment like
    if removeLikes.get():
        removed_likes = 0

        list_no = 0

        while True:
            if not is_program_run:
                sys.exit()
            list_url = like_comment_list_url + str(list_no)
            list_no += 0 # 공감의 경우 1페이지 공감 철회시 2페이지의 공감이 1페이지로 이동하여 리스트 번호 증가 필요가 없습니다.

            list_page = cc.get(list_url)

            if not check_end(list_page):
                break

            soup = bs(list_page.text, 'html.parser')
            link = soup.select('div.list_title > a.list_subject')
            csrf = cc.set_csrf(list_page, {})

            for cell in link:
                board, article_sn, comment_sn = cc.extract_like_comment(cell)
                cc.cancel_like_comment(board, article_sn, comment_sn, csrf)

                removed_likes += 1
                messageLabel.config(text = '댓글 공감을 철회중입니다. 남은 예상 시간 : ' + cc.remaining_time_like(removed_likes))
                

    #remove article like
        list_no = 0
        
        while True:
            if not is_program_run:
                sys.exit()
            list_url = like_article_list_url + str(list_no)
            list_no += 0 # 공감의 경우 1페이지 공감 철회시 2페이지의 공감이 1페이지로 이동하여 리스트 번호 증가 필요가 없습니다.

            list_page = cc.get(list_url)

            if not check_end(list_page):
                break

            soup = bs(list_page.text, 'html.parser')
            link = soup.select('div.list_title > a.list_subject')
            csrf = cc.set_csrf(list_page, {})

            for cell in link:
                board, article_sn = cc.extract_like_article(cell)
                cc.cancel_like_article(board, article_sn, csrf)

                removed_likes += 1
                messageLabel.config(text = '게시글 공감을 철회중입니다. 남은 예상 시간 : ' + cc.remaining_time_like(removed_likes))


    #remove comment
    if removeComments.get():
        removed_comments = 0
        list_no = 0;

        while True:
            if not is_program_run:
                sys.exit()
            list_url = comment_list_url + str(list_no)
            list_no +=1
            
            list_page = cc.get(list_url)

            if not check_end(list_page):
                break

            soup = bs(list_page.text, 'html.parser')
            link = soup.select('div.list_title > a.list_subject')
            csrf = cc.set_csrf(list_page, {})

            for cell in link:
                board, article_sn, comment_sn = cc.extract_comment(cell)
                cc.delete_comment(board, article_sn, comment_sn, csrf)

                removed_comments += 1
                messageLabel.config(text = '댓글을 삭제하는 중입니다. 남은 예상 시간 : ' + cc.remaining_time_comment(removed_comments, list_no))


    #remove article
    if removeArticles.get():
        removed_articles = 0
        list_no = 0

        while True:
            if not is_program_run:
                sys.exit()
            
            list_url = article_list_url + str(list_no)
            list_no += 1

            list_page = cc.get(list_url)

            if not check_end(list_page):
                break

            soup = bs(list_page.text, 'html.parser')
            link = soup.select('div.list_title > a.list_subject')
            csrf = cc.set_csrf(list_page, {})

            for cell in link:
                board, article_sn = cc.extract_article(cell)
                cc.delete_article(board, article_sn, csrf)
                
                removed_articles += 1
                messageLabel.config(text = '게시글을 삭제하는 중입니다. 남은 예상 시간 : ' + cc.remaining_time_article(removed_articles, list_no))

                
    messageLabel.config(text = "요청한 작업을 모두 완성하였습니다.")





tk.title("FineAsh(Clien)")
tk.configure(background='royalblue')
tk.iconbitmap(r'' + os.path.join(os.getcwd(), 'clien.ico'))


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
messageLabel = Label(messageFrame, text = "FineAsh(CLIEN) 20240402")
messageLabel.pack()

loginFrame = Frame(tk)
loginFrame.configure(background='deepskyblue')
loginFrame.pack(padx = 10, pady = 10)

loginIDPWFrame = Frame(loginFrame)
loginIDPWFrame.configure(background='deepskyblue')
loginIDPWFrame.pack(padx = 10, pady = 10)

loginIDLabel = Label(loginIDPWFrame, text="아이디", background='deepskyblue')
loginIDLabel.grid(row=1, column=0)
loginIDEntry = Entry(loginIDPWFrame, textvariable=loginID, width=20)
loginIDEntry.grid(row = 1, column = 1)

loginPWLabel = Label(loginIDPWFrame, text = "비밀번호", background='deepskyblue')
loginPWLabel.grid(row = 2, column = 0)
loginPWEntry = Entry(loginIDPWFrame, textvariable=loginPW, width=20, show="*")
loginPWEntry.grid(row = 2, column = 1)

loginButton = Button(loginFrame, text = "로그인", command= lambda: login(loginID.get(), loginPW.get()))
loginButton.pack()

optionFrame = Frame(tk)
optionFrame.configure(background='deepskyblue')
optionFrame.pack(padx = 10, pady = 10);

option1 = Checkbutton(optionFrame, text = "공감", variable = removeLikes, background = 'deepskyblue')
option2 = Checkbutton(optionFrame, text = "글  ", variable = removeArticles, background = 'deepskyblue')
option3 = Checkbutton(optionFrame, text = "댓글", variable = removeComments, background = 'deepskyblue')

option1.grid(row = 0, column = 0)
option2.grid(row = 0, column = 1)
option3.grid(row = 0, column = 2)

removeContentsThread = threading.Thread(target=removeContents)
removeButton = Button(tk, text = "삭제", state = 'disabled', command = lambda: removeContentsThread.start())
removeButton.pack()

if cc.is_login():
    cc.set_info()
    loginButton['text'] = "안녕하세요 " + cc.nickname + "님"
    loginID.set(cc.signin_id)
    loginPW.set(' ' * 8)
    loginButton['state'] = 'disabled'
    removeButton['state'] = 'normal'

tk.mainloop()


is_program_run = False
