## .gitignore 파일
# -> 깃에 올릴 때 제외하고 싶은 파일 설정(보안 필요한 경우나 쓸모 없는 파일 제외)
# Git으로 관리하지 않을 파일이나 폴더를 지정하는 설정 파일

## echo "# aio4_class" >> README.md
# -> README.md 파일 끝에 # aio4_class라는 글을 추가
# -> echo: 글자를 출력
# -> >>: 출력한 글자를 파일 끝에 추가
# -> README.md: 프로젝트 소개를 적는 파일
# -> # aio4_class: Markdown 문법으로 작성한 큰 제목
# -> 파일이 없으면 새로 만들고, 같은 명령을 반복하면 제목이 계속 추가됨 

## git init
# -> 현재 폴더를 Git으로 관리하기 시작
# -> 프로젝트를 처음 설정할 때 한 번 실행

## git branch -M main
# -> 현재 브랜치 이름을 main으로 변경
# -> 브랜치는 작업 이력을 나누어 관리하는 작업 흐름
# -> 처음에는 main을 기본 작업 공간이라고 생각
# -> -M은 같은 이름이 있어도 강제로 이름을 바꾸는 옵션

## git remote add origin 주소
# ex) git remote add origin https://github.com/mj-git-memory/aio4_class.git
# -> 로컬 저장소에 GitHub 저장소 주소를 등록
# -> remote: 원격 저장소 연결 관리
# -> add: 연결 추가
# -> origin: 이 주소에 붙이는 별명
# -> origin은 특별한 비밀번호 같은 것이 아니라, 관례적으로 쓰는 이름
# -> 마지막 URL: GitHub 저장소 주소

## git remote remove origin 
# -> origin이라는 원격 저장소 연결 정보를 삭제
# -> 내 컴퓨터의 코드나 GitHub 저장소 자체가 삭제되는 것은 아님 
## git remote set-url origin 새_저장소_URL
# -> 주소만 잘못 등록했다면 삭제 후 다시 추가하기보다 다음처럼 바꾸면 됨 
## git remote -v
# -> 연결된 주소를 확인하

## git add README.md
# -> README.md의 변경 내용을 다음 커밋에 포함하도록 선택
# -> 이 준비 영역을 스테이징 영역이라고 함 
## git add day4/day4_git.py
# -> 특정 파일만 선택
## git add .
# -> 현재 폴더와 하위 폴더의 변경 사항을 한꺼번에 선택

## git commit -m "day4 Git 복습 내용 정리"
# -> git add로 선택한 변경 사항을 내 컴퓨터의 Git 저장소에 기록
# -> -m: 커밋 설명을 함께 작성하는 옵션
# -> "day4 Git 복습 내용 정리": 이번 변경에 대한 설명
# -> 커밋만으로 GitHub에 업로드되지는 않음 

## git push -u origin main
# -> 로컬의 main 브랜치에 있는 커밋을 origin이라는 원격 저장소로 업로드
# -> -u는 로컬 main과 원격 main을 연결해 두는 옵션
# 연결을 설정한 뒤에는 보통 git push 처럼 쓸 수 있음 

## git pull origin main 
# -> 원격 저장소의 main 브랜치 변경 사항을 가져와서 현재 로컬 브랜치에 통합
# -> 다른 컴퓨터나 팀원이 GitHub에 올린 변경 사항을 내 작업 폴더에 반영할 때 사용
# -> 같은 부분을 서로 다르게 수정했다면 충돌을 해결해야 함 

## git clone 주소 
# ex) git clone https://github.com/skn29teacher/ai4_section01.git
# -> 기존 GitHub 저장소를 내 컴퓨터에 새 폴더로 내려받음 
# -> 코드뿐 아니라 Git 이력과 origin 연결도 함께 가져오기 때문에, 
# -> 복제한 폴더에서는 git init과 git remote add origin을 다시 실행할 필요가 없음 

# ------------------------------------------------------------------------------------
### 1. 로컬 pc의 작업 폴더 설정
## -> cd ~/Downloads/AIO_4_class : 터미널에서 프로젝트 폴더로 이동
## -> git status : 현재 위치와 Git 상태 확인. 
# -> not a git repository가 나오면 아직 Git 저장소가 아니라는 뜻
# -> 이미 브랜치나 변경 파일 목록이 나온다면 Git이 설정된 폴더

### 2. git 원격 repository 설정
## -> GitHub 웹사이트에서 새 저장소를 만듦
# -> 저장소 이름(Repository name) 설정. ex) aio4_class
# -> 로컬 프로젝트를 처음 올리는 연습에서는 GitHub 저장소 생성 시 
# -> README, .gitignore, 라이선스를 추가하지 않은 빈 저장소로 만들면 진행이 간단 

### 3. 커밋 작성자 정보 설정
## -> git config --global user.name "본인 이름" ex) mjlee
## -> git config --global user.email "본인 이메일" -> 이메일은 GitHub에 등록된 이메일
# -> --global : 컴퓨터의 여러 Git 프로젝트에 공통으로 적용한다는 뜻

### 4. Git 저장소 초기화 
## -> git init  
# -> 이 단계에서 .gitignore도 준비
# -> 비밀번호나 API 키가 담긴 파일을 git add하기 전에 제외

### 5. 기본 브랜치 이름 설정 (branch 이름을 main으로 변경)
## -> git branch -M main

### 6. GitHub 저장소 연결(repository 연결)
## -> git remote add origin https://github.com/mj-git-memory/aio4_class.git
# -> git remote -v : 연결 확인

### 7. 코드 커밋
## -> git status : 변경 사항 확인
## -> git add . : 커밋할 파일 선택
## -> git status
## -> git commit -m "first commit" : 선택한 파일 확인하고 커밋

### 8. 푸시 
## -> git push -u origin main
# -> 완료되면 GitHub 저장소 페이지에서 파일을 확인

#----------- 복습 ------------------------------------------------------- 
# 깃은 내 컴퓨터에서 코드 변경 이력을 관리하는 도구
#  GitHub는 그 코드를 인터넷에 저장하고 공유하는 서비스

# 파일 수정    → git add       → git commit    → git push
#              :올릴 변경 선택    :로컬에 기록       :GitHub에 업로드

# | 상황                          | 명령어                  |
# |------------------------------|-----------------------|
# | 현재 파일 변경 상태 확인           | `git status`          |
# | 커밋할 변경 사항 선택             | `git add 파일명`        |
# | 선택한 변경 사항을 로컬에 기록      | `git commit -m "설명"`  |
# | 로컬 커밋을 GitHub에 올리기       | `git push`            |
# | GitHub의 변경 사항 가져와 통합하기  | `git pull`            |
# | 기존 저장소를 새 폴더로 내려받기     | `git clone 주소`       |
# |------------------------------|-----------------------|