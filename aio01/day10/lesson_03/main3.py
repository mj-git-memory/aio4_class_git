# 한 사용자의 점수를 수정하고, 다른 사용자를 삭제하는 프로그램
# 의도한 동작은 “수정과 삭제가 모두 성공하면 저장하고, 하나라도 실패하면 둘 다 취소하기” 
# 그런데 현재는 수정 직후 commit()을 해서, 나중에 삭제가 실패해도 수정 내용은 남는 버그가 있음

"""수정과 삭제를 한 묶음으로 처리한다. 중간 commit에 의도한 버그가 있다."""
# -> 한 묶음으로 처리한다는 것은 여러 DB 작업을 하나의 트랜잭션으로 처리한다는 의미
# 모두 성공하면 commit()으로 확정
# 중간에 실패하면 rollback()으로 아직 확정하지 않은 변경을 취소

import argparse
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
# 잠깐 사용할 임시 폴더를 만드는 도구
# -> 이 프로그램에서는 임시 폴더 안에 실습용 DB를 만들고, 작업이 끝나면 폴더와 DB 파일을 자동으로 정리


# DB 파일 경로를 받아 테이블과 초기 사용자 데이터를 준비
## DB 준비 함수
def prepare_database(db_path):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        connection.execute(
            "CREATE TABLE users3 (id INTEGER PRIMARY KEY, "
            # -> IF NOT EXISTS가 없으므로, 같은 DB에 users3가 이미 있다면 오류가 발생
            "nickname TEXT NOT NULL, points INTEGER NOT NULL)"
        )
        connection.executemany(
        # executemany() : 목록에 있는 각 튜플을 사용해 같은 SQL을 반복 실행
            "INSERT INTO users3 (id, nickname, points) VALUES (?, ?, ?)",
            [(1, "민지", 80), (2, "준호", 95), (3, "수아", 70)],
        )
        connection.commit() # 테이블 생성과 사용자 추가를 확정
    finally:
        connection.close()

## 사용자 조회 함수 
# DB 파일 경로를 받아 사용자 목록을 반환
def read_users(db_path):
    # DB에 새로 연결
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        return connection.execute(
            "SELECT id, nickname, points FROM users3 ORDER BY id"
        ).fetchall()
        # .fetchall() : 조회한 모든 행을 Python 리스트로 가져옴
    finally:
        connection.close()

## 수정과 삭제 함수
def apply_changes(db_path, update_id, points, delete_id):
    connection = sqlite3.connect(db_path, autocommit=False)
    try:
        # updated에는 사용자 목록이 아니라, SQL 실행 결과를 확인할 수 있는 커서 객체가 들어감 
        updated = connection.execute(
            "UPDATE users3 SET points = ? WHERE id = ?", (points, update_id)
        )
        if updated.rowcount != 1:
        # rowcount : SQL 실행 결과인 커서 객체의 속성(SQL이 몇 행을 처리했는지 알려줌) 
        # (속성은 updated.rowcount처럼 괄호 없이 사용)
        # 수정 SQL이 처리한 행 수가 정확히 1개인지 확인
        # -> 존재하는 번호이면 보통 1
        # -> 존재하지 않는 번호이면 0

            raise ValueError("수정 대상은 정확히 1명이어야 합니다.")
            # 처리한 행이 1개가 아니면 오류를 발생
            # 해당 사용자가 없으면 이 오류가 발생. 이후 삭제는 실행하지 않고 except로 이동
        connection.commit() # 아래의 삭제를 실행하지 않았는데 점수 수정부터 확정(버그의 원인)
                            # -> 이후 삭제에 실패해도 이 수정은 rollback()으로 되돌릴 수 없음
                            # -> 수정과 삭제를 한 묶음으로 처리하려면 두 작업 사이의 commit()을 제거하고 마지막에 한 번만 확정해야 함 

        # 지정한 번호의 사용자를 삭제. deleted도 SQL 실행 결과를 확인할 커서 객체
        deleted = connection.execute(
            "DELETE FROM users3 WHERE id = ?", 
            (delete_id,) # 값 하나를 담은 튜플. 튜플로 만들기 위해 쉼표가 필요
        )
        if deleted.rowcount != 1:
        # 삭제한 행이 정확히 1개인지 확인.  
            raise ValueError("삭제 대상은 정확히 1명이어야 합니다.")
            # 없는 번호를 전달하면 삭제 행 수가 0이므로 오류가 발생
        connection.commit() # 삭제까지 성공하면 현재 변경 내용을 확정
        
        return updated.rowcount, deleted.rowcount # 수정 행 수와 삭제 행 수를 튜플로 반환 # (1, 1)
    
    except (ValueError, sqlite3.Error): # “이런 종류의 오류가 나면 여기서 처리하겠다.”
        connection.rollback() # 현재 트랜잭션에서 아직 확정하지 않은 DB 변경을 취소
        raise # 방금 처리 중인 오류를 다시 발생시켜, 함수를 호출한 곳에도 알림

    finally:
        connection.close()

# ValueError	수정 또는 삭제 대상이 없음
# sqlite3.Error	SQL 실행 등에서 DB 오류 발생

## 실행 옵션 등록
if __name__ == "__main__":
    parser = argparse.ArgumentParser() # 터미널 옵션을 해석할 객체를 만듦
    parser.add_argument("--update-id", type=int, default=1) # 점수를 수정할 사용자 번호를 받음
    parser.add_argument("--points", type=int, default=90) # 새 점수를 받음 
    parser.add_argument("--delete-id", type=int, default=3) # 삭제할 사용자 번호를 받음 
    args = parser.parse_args() # 실제로 전달한 옵션을 읽음
    failed = False # 실패 여부를 기록하는 변수. 처음에는 실패하지 않았으므로 False
    with TemporaryDirectory() as folder:
    # 임시 폴더(작업하는 동안만 사용하고, 끝나면 자동으로 지우는 폴더)를 만들고, 그 경로를 folder에 저장
    # -> with 블록을 벗어나면 임시 폴더와 그 안의 파일이 자동으로 정리됨
        db_path = Path(folder) / "main3.db"
        # 임시 폴더 안에 있는 main3.db의 경로를 만듦 (임시 폴더 안에 사용할 DB 파일 경로를 만듦)
        # / : 경로를 연결하는 연산
        prepare_database(db_path) # 임시 DB에 테이블과 사용자 3명을 준비
        print("변경 전:", read_users(db_path)) # 변경 전 데이터를 조회해서 출력
        try:
            counts = apply_changes(db_path, args.update_id, args.points, args.delete_id)
            # 함수가 성공해서 반환하면 -> counts에는 (1, 1)이 들어 있음 : 수정 1행, 삭제 1행
            # 입력된 번호와 점수로 수정·삭제를 실행
            # 터미널 옵션         Python에서 접근
            # --update-id      args.update_id
            # --delete-id      args.delete_id
            print("수정·삭제 행 수:", counts)

        except ValueError as exc:
        # apply_changes()에서 다시 발생시킨 ValueError를 받음. 오류 객체에는 exc라는 이름을 붙임
        # -> 이 except는 ValueError만 처리. sqlite3.Error는 여기서 잡지 않으므로 발생하면 오류 메시지와 함께 실행이 중단됨 
            failed = True # 실패했다는 사실을 기록
            print("오류:", exc)
        print("재연결 결과:", read_users(db_path)) # DB에 새로 연결해서 실제로 남은 데이터를 출력
    raise SystemExit(1 if failed else 0) 
    # SystemExit : 프로그램 종료에 사용하는 특별한 예외
    # -> 숫자 0과 1은 화면에 출력할 값이 아니라 터미널이나 다른 프로그램에 전달하는 종료 코드
    # 프로그램을 종료하면서 종료 코드를 전달 (사용하는 이유는 다른 프로그램이 출력 문장을 읽지 않고도 성공 여부를 판단할 수 있게 하기 위해서)
    # -> raise는 프로그램을 종료하기 위한 SystemExit를 발생시킵
    # failed	종료 코드	의미
    # True	    1	      실패
    # False	    0	      정상 종료


## python main3.py
# -> 기본 옵션으로 실행하면 두 작업이 모두 성공
# 변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
# 수정·삭제 행 수: (1, 1)
# 재연결 결과: [(1, '민지', 90), (2, '준호', 95)]

## python main3.py --delete-id 999
# -> 문제는 없는 사용자를 삭제하려 할 때 나타납니다.
# 민지의 점수를 80 → 90으로 수정합니다.
# 중간 commit()으로 수정을 확정합니다.
# 999번 사용자 삭제를 시도하지만 대상이 없습니다.
# ValueError가 발생하고 rollback()을 실행합니다.
# 이미 확정한 민지의 점수는 그대로 남습니다.
# 변경 전: [(1, '민지', 80), (2, '준호', 95), (3, '수아', 70)]
# 오류: 삭제 대상은 정확히 1명이어야 합니다.
# 재연결 결과: [(1, '민지', 90), (2, '준호', 95), (3, '수아', 70)]

## -> 수정과 삭제를 한 묶음으로 처리하려면 두 작업 사이의 commit()을 제거하고 마지막에 한 번만 확정해야 함