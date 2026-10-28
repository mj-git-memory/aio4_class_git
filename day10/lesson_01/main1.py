### SQLite DB에 사용자를 추가한 뒤, 같은 연결과 새 연결에서 조회한 결과를 비교하는 프로그램

import argparse
# argparse : 터미널에서 프로그램을 실행할 때 프로그램에 필요한 값을 함께 전달할 수 있음. 
# ex) python main.py --name 수진 : "main.py를 실행하고, 이름으로 수진을 사용해 줘”라는 뜻
# -> Python이 --name의 의미를 자동으로 아는 것은 아님. 코드에서 argparse를 이용해 알려줘야 함.
from pathlib import Path
# Path : 파일과 폴더 경로를 다룸
# -> 아래에서 기본 DB 파일 위치를 정할 때 사용
import sqlite3
# sqlite3 : Python에서 SQLite 데이터베이스를 사용할 수 있게 해주는 모듈

def save_user(db_path, nickname) : 
    # db_path :	사용할 DB 파일 경로. ex)	"practice.db"
    # nickname : 저장할 사용자 이름. ex) "민지"
    connection = sqlite3.connect(db_path, autocommit=False)
    # 지정한 DB 파일에 연결하고, 연결 객체를 connection에 저장
    # DB 파일이 없으면 생성
    # autocommit=False : 변경 내용을 자동으로 확정하지 않고, commit()으로 직접 확정하겠다는 설정
    # -> commit() 없이 연결을 닫으면, 확정하지 않은 추가 내용은 취소
    
    try : 
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users ("\
            "id INTEGER PRIMARY KEY, " \
            "nickname TEXT NOT NULL)"
            # users라는 테이블이 없으면 생성. 이미 있으면 기존 테이블을 사용
        )
        connection.commit() # 지금까지의 변경 내용을 확정 -> 이 시점에는 테이블만 만들었으므로 사용자 추가까지 확정하는 것은 아님
        connection.execute(
            "INSERT INTO users (nickname) VALUES (?)", (nickname,)
            # users 테이블의 nickname 열에 이름을 추가
            # ?는 값을 넣을 자리
            # (nickname,)은 그 자리에 전달할 값을 담은 튜플
            # 값이 하나인 튜플은 뒤에 쉼표가 필요. (nickname)은 튜플이 아님 
            # -> nickname 값을 SQL 문자열에 직접 이어 붙이지 않고 별도로 전달하므로, 
            # -> O'Neil처럼 따옴표가 있는 이름도 올바르게 처리할 수 있음 
        )
        # 사용자 목록을 조회하고, 결과 전체를 rows에 저장
        rows = connection.execute(
            "SELECT id, nickname FROM users ORDER BY id"
        ).fetchall()
        # .fetchall() :	조회 결과 전체를 리스트로 가져옴
        
        connection.commit() # 지금까지의 변경 내용을 확정 (-> INSERT로 추가한 사용자 저장 확정)
        print(f'rows: {rows}')
        return rows 
        
        # -> 예를 들어 rows에는 다음 값이 들어감. [(1, '민지'), (2, '수진')] : 바깥은 리스트이고, 각 행은 튜플
        # 조회한 목록을 함수를 호출한 곳에 돌려줌 
  
    finally : 
        connection.close()

def read_users(db_path):
    # DB 파일 경로를 받아 사용자 목록을 조회하는 함수를 정의
    connection = sqlite3.connect(db_path, autocommit=False)
    # DB 파일에 새 연결을 만듦. save_user()에서 사용한 연결과는 다른 연결
    try:
        # 연결을 사용한 조회 작업을 시작
        return connection.execute(
            "SELECT id, nickname FROM users ORDER BY id"
        ).fetchall()
        # .fetchall() :	조회 결과 전체를 리스트로 가져옴
    finally:
        connection.close()


# 이 파일을 직접 실행했을 때만 아래 코드를 실행
# -> 다른 파일에서 import main으로 가져올 때는 아래 실행 부분이 동작하지 않음. 
if __name__ == '__main__' : 

    parser = argparse.ArgumentParser()
    # 터미널 실행 옵션을 처리할 객체를 만듦.
    # 옵션을 읽고 해석할 담당자를 만듦. 여기서는 parser라는 이름을 붙임

    parser.add_argument("--db", default=str(Path(__file__).with_name('practice.db')))
    # --db 옵션을 등록. 옵션을 생략하면 main.py와 같은 폴더에 있는 practice.db를 사용
    # __file__ : 현재 Python 파일의 경로
    print(f'__file__: {__file__}')
    print(f'str(__file__): {type(__file__)}')
    # Path(__file__) : 그 경로를 Path 객체로 표현
    print(f'Path(__file__): {Path(__file__)}')
    print(f'type(Path(__file__)): {type(Path(__file__))}')
    # .with_name('practice.db') : 같은 폴더에서 파일 이름을 practice.db로 바꾼 경로
    # str(...): 경로를 문자열로 변환
    parser.add_argument("--name", default='민지')
    # --name 옵션을 등록. 입력하지 않으면 "민지"를 사용.
    
    args = parser.parse_args()
    # 터미널에서 전달한 옵션을 실제로 읽음 -> 실제로 입력한 실행 옵션을 해석하여 args에 저장
    
    print("연결 안에서: ", save_user(args.db, args.name))
    # ex) python main.py --db test.db --name 수진
    # -> save_user()를 실행. 사용자를 추가하고, 그 연결 안에서 조회한 결과를 출력
    # -> args.db    # "test.db"
    # -> args.name  # "수진"
    
    # print(args.name) : 읽은 이름을 출력
    print("다시 연결하면: ", read_users(args.db))
    # -> read_users()로 새 연결을 열어 조회한 결과를 출력



# python main.py --db test.db
# python main.py --db test.db --name honggildong
# python main.py --name 수진 --db test.db
# python main.py --name 홍길동
# -> 실행할 때마다 코드 속 이름이나 DB 경로를 고치지 않고, 터미널 명령으로 사용할 값을 바꾸기 위해 argparse를 사용

# 함수·메서드       	    역할
# save_user()	        테이블 준비 → 사용자 추가 → 목록 조회 → 결과 반환
# read_users()	        새 연결에서 사용자 목록 조회
# sqlite3.connect()	    DB 파일에 연결
# connection.execute()	SQL 실행
# .fetchall()	        조회 결과 전체를 리스트로 가져오기
# connection.commit()	DB 변경 내용을 확정
# connection.close()	DB 연결 종료
# parser.add_argument()	실행 옵션 등록
# parser.parse_args()	입력한 실행 옵션 해석