# ClienRemover
클리앙의 자신의 모든 글 + 댓글 삭제

본 게시글은 https://beomi.github.io/2017/01/20/HowToMakeWebCrawler-With-Login/ 의 도움을 받아 작성되었습니다.

회원탈퇴 이전 등록한 게시물을 지우기 위해서 클리앙 글 삭제 프로그램을 검색했습니다.
아래와 같은 글 한 건이 있었지만 아쉽게도 클리앙이 개편되면서 더는 동작하지는 않아 새로 만들어봤습니다.

https://www.clien.net/service/board/lecture/6411713

기능은 다음과 같습니다.
1. 댓글을 삭제합니다.
2. 글을 삭제합니다.

아무거나 질문 게시판의 경우 댓글이 달려 있으면 클리앙 정책상 삭제가 불가능하여, 제 프로그램으로도 삭제 불가능합니다.
내용만 수정하여 날리는 기능은 만들지 않았기 때문에.. 해당 게시판에서 작성자 검색 후 수정해주시면 되겠습니다.

실행에는 Python 3, requests, BeautifulSoup 가 필요하며, 윈도우 10, 64bit에서만 시도해봤습니다. 아마 다른 OS에서도 정상적으로 실행될 것이라고 예상됩니다.

Python 설치 : https://www.python.org/downloads/
requests 설치 : pip install requests
BeautifulSoup 설치 : pip install beautifulsoup4

requests 설치와 BeautifulSoup 설치는 Python 설치 이후에 콘솔에서 명령어 입력으로 설치 가능합니다. pip 대신에 pip3으로 입력해야 할 수도 있습니다.


사용방법
첨부파일 압축 해제 후 메모장 등의 텍스트 편집기로 파일을 열어주세요.
#클리앙 아이디 입력 왼쪽에 'your id' 안에 클리앙 아이디를 적어주세요.
#클리앙 비밀번호 입력 왼쪽에 'your pw' 안에 클리앙 비밀번호를 적어주세요.

예를 들어 아이디가 clien이고, 비밀번호가 1234이면,

#user information
user_info = {
    'userId': 'your id',#클리앙 아이디 입력
    'userPassword': 'your pw'#클리앙 비밀번호 입력
}

#user information
user_info = {
    'userId': 'clien',#클리앙 아이디 입력
    'userPassword': '1234'#클리앙 비밀번호 입력
}

이런 식으로 수정해주신 다음 저장하시면 됩니다.

그다음에 해당 파일을 exe 파일을 실행하는 것처럼 더블클릭하시면 됩니다.

감사합니다.
