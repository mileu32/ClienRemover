import os
import pickle
import re
import requests
import time

from bs4 import BeautifulSoup as bs



class ClienClient:
	url = {
		'mypage' : 'https://www.clien.net/service/mypage/myInfo',
		'main' : 'https://www.clien.net',
		'login' : 'https://www.clien.net/service/login',
		'info' : 'https://www.clien.net/service/popup/userInfo/basic/', # + signin_id
		'api' : 'https://www.clien.net/service/api/'
	}

	def __init__(self, user_agent: str = 'FineAsh 20240401', auto_login: bool = True, release_mode: bool = True):
		self.session = requests.Session()
		self.session.headers.update({'User-Agent': user_agent})
		self.auto_login = auto_login
		self.release_mode = release_mode # debug 모드에서는 테스트당(cm_test)에 대해서만 작업 실행(release_mode=False)

		self.nickname = '회원'
		self.signin_id = None

		# sleep time margin
		self.margin = 4
		self.margin_s = 1

		self.num_symph = -1
		self.num_article = -1
		self.num_article_page = -1
		self.num_comment = -1
		self.num_comment_page = -1

		if self.auto_login:
			try:
				with open('fine.ash', 'rb') as f:
					cookies = pickle.load(f)
					self.session.cookies.update(cookies)
			except FileNotFoundError:
				print('알림: 이전에 저장된 로그인 정보가 없습니다.')

	def get(self, url, short_sleep = False):
		page = self.session.get(url)
		if short_sleep:
			time.sleep(self.margin_s)
		else:
			time.sleep(self.margin)

		return page

	def post(self, url, data, short_sleep = False):
		response = self.session.post(url, data=data)
		if short_sleep:
			time.sleep(self.margin_s)
		else:
			time.sleep(self.margin)

		return response

	# 나의글 리스트의 셀에서 정보 추출
	def extract_comment(self, cell):
		href = cell.get('href')

		if href == '#': # 원 게시글이 삭제된 댓글 처리
			# onclick="app.delComment('cm_test',18684182,147617486);"
			onclick = cell.get('onclick')
			onclick = onclick.replace('app.delComment(', '').replace(');', '').replace("'", "")
			board, article_sn, comment_sn = onclick.split(',')
			return (board, article_sn, comment_sn)

		# href="/service/board/news/18681225?c=true#147592151"
		href = href.replace('/service/board/', '')
		board, article_sn = href.split('?')[0].split('/')
		comment_sn = href.split('#')[1]
		return (board, article_sn, comment_sn)

	def extract_article(self, cell):
		# href="/service/board/park/18670953"
		href = cell.get('href')
		board, article_sn = href.replace('/service/board/', '').split('/')
		return (board, article_sn)

	def extract_like_comment(self, cell):
		href = cell.get('href')

		if href == '#': # 원 게시글이 삭제된 댓글 처리
			# onclick="app.cancleLikeComment('park',18681136,147585815);"
			onclick = cell.get('onclick')
			onclick = onclick.replace('app.cancleLikeComment(', '').replace(');', '').replace("'", "")
			board, article_sn, comment_sn = onclick.split(',')
			return (board, article_sn, comment_sn)

		# href="/service/board/lecture/18680558?c=true#147583939"
		href = href.replace('/service/board/', '')
		board, article_sn = href.split('?')[0].split('/')
		comment_sn = href.split('#')[1]
		return (board, article_sn, comment_sn)

	def extract_like_article(self, cell):
		# href="/service/board/park/18681320"
		href = cell.get('href')
		board, article_sn = href.replace('/service/board/', '').split('/')
		return (board, article_sn)

	# 클리앙 글 및 댓글 삭제, 공감 철회 요청 수행
	def delete_comment(self, board, article_sn, comment_sn, csrf):
		try:
			# post https://www.clien.net/service/api/board/cm_test/18670833/comment/delete/147549910
			api = self.url['api'] + f'board/{board}/{article_sn}/comment/delete/{comment_sn}'
			if self.release_mode or 'cm_test' in api:
				req = self.post(api, data=csrf, short_sleep=True)
		except:
			print('오류: delete_comment 실행에 실패했습니다.', board, article_sn, comment_sn)

	def delete_article(self, board, article_sn, csrf):
		try:
			# post https://www.clien.net/service/api/board/cm_test/delete, data: boardSn=18670833
			api = self.url['api'] + f'board/{board}/delete'
			data = {'boardSn' : article_sn}
			if self.release_mode or 'cm_test' in api:
				req = self.post(api, data={**data, **csrf}, short_sleep=True)
		except:
			print('오류: delete_article 실행에 실패했습니다.', board, article_sn)

	def cancel_like_comment(self, board, article_sn, comment_sn, csrf):
		try:
			# post https://www.clien.net/service/api/comment/like/lecture/18667297/147594619
			api = self.url['api'] + f'comment/like/{board}/{article_sn}/{comment_sn}'
			if self.release_mode or 'cm_test' in api:
				req = self.post(api, data=csrf, short_sleep=True)
				print(req, api)
		except:
			print('오류: cancel_like_comment 실행에 실패했습니다.', board, article_sn, comment_sn)

	def cancel_like_article(self, board, article_sn, csrf):
		try:
			# post https://www.clien.net/service/api/board/like/cm_mac/18683167/delete
			api = self.url['api'] + f'board/like/{board}/{article_sn}/delete'
			if self.release_mode or 'cm_test' in api:
				req = self.post(api, data=csrf, short_sleep=True)
		except:
			print('오류: cancel_like_article 실행에 실패했습니다.', board, article_sn)

	def remaining_time_like(self, removed_count):
		time_left = ((self.num_symph - removed_count) * self.margin + (((self.num_symph - removed_count) + 19) // 20) * self.margin) * 1.05
		return self.convert_seconds(time_left)

	def remaining_time_comment(self, removed_count, page_count):
		time_left = ((self.num_comment - removed_count) * self.margin + (self.num_comment_page - page_count) * self.margin) * 1.05
		return self.convert_seconds(time_left)

	def remaining_time_article(self, removed_count, page_count):
		time_left = ((self.num_article - removed_count) * self.margin + (self.num_article_page - page_count) * self.margin) * 1.05
		return self.convert_seconds(time_left)

	def convert_seconds(self, n):
	    # 시간, 분, 초 계산
	    hours = int(n // 3600)
	    minutes = int((n % 3600) // 60)
	    seconds = int((n % 3600) % 60)
	    
	    # 시간, 분, 초 조합으로 문자열 생성
	    if hours > 0:
	        return f'{hours}시간 {minutes}분 {seconds}초'
	    elif minutes > 0:
	        return f'{minutes}분 {seconds}초'
	    else:
	        return f'{seconds}초'

	def set_csrf(self, page, param):
		html = page.text
		soup = bs(html, 'html.parser')
		csrf = soup.find('input', {'name': '_csrf'})
		return {**param, **{'_csrf': csrf['value']}}

	def set_info(self):
		if self.signin_id is not None:
			page = self.get(self.url['info'] + self.signin_id, short_sleep=True)

			soup = bs(page.text, 'html.parser')
			symph = str(soup.select('div.popup_content > ul.user_activity_etc > li > span:nth-child(2)')[0])
			self.num_symph = int(''.join(re.findall(r'\d+', symph)))

			article = soup.find('span', class_='user_article').text.replace(',', '')
			article_delete = soup.find('span', class_='user_article_delete').text.replace(',', '')
			article_admin_delete = soup.find('span', class_='user_article_admin_delete').text.replace(',', '')
			self.num_article = int(article)
			self.num_article_page = (int(article) + int(article_delete) + int(article_admin_delete) + 19) // 20


			comment = soup.find('span', class_='user_comment').text.replace(',', '')
			comment_delete = soup.find('span', class_='user_comment_delete').text.replace(',', '')
			comment_admin_delete = soup.find('span', class_='user_comment_admin_delete').text.replace(',', '')
			self.num_comment = int(comment)
			self.num_comment_page = (int(comment) + int(comment_delete) + int(comment_admin_delete) + 19) // 20

		else:
			print('오류: 로그인 정보가 없어 공감 횟수 및 글 댓글 작성 횟수를 불러올 수 없습니다.')

	def login(self, signin_id, signin_pw) -> bool:
		if self.is_login():
			return True

		user = {}
		user['userId'] = signin_id
		user['userPassword'] = signin_pw
		user['deviceId'] = ''
		user['totpcode'] = ''

		main_page = self.get(self.url['main'], short_sleep=True)

		user = self.set_csrf(main_page, user)
		login_req = self.session.post(self.url['login'], data = user)

		if self.is_login():
			if self.auto_login:
				with open('fine.ash', 'wb') as f:
					pickle.dump(self.session.cookies, f)
				return True

		return False

	def is_login(self) -> bool:
		page = self.get(self.url['mypage'], short_sleep=True)

		if 'login' in page.url:
			if os.path.exists('fine.ash'):
				os.remove('fine.ash')
			#self.session.cookies.clear()
			return False

		try:
			soup = bs(page.text, 'html.parser')
			self.signin_id = soup.select('#myInfoForm > table > tr > td > input')[0].get('value').strip()
			self.nickname = soup.select('#myInfoForm > table > tr > td > input')[1].get('value').strip()
			return True
		except:
			return False
