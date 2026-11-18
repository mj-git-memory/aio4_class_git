import json
from pathlib import Path
from getpass import getpass

import psycopg  # 설치:pip install "psycopg[binary]" / 제거:python -m pip uninstall pycopg

config_path = Path(__file__).with_name('config.json')
print(config_path) # /Users/imijeong/Downloads/AIO_4_class/day11/config.json
config = json.loads(config_path.read_text(encoding='utf-8')) # 


with psycopg.connect(
    host = config['host'],
    port = config['port'],
    dbname =  config.get('dbname', config.get('database')),
    user = config['user'],
    password = getpass('supabase 비밀번호를 입력하세요:'),
    # password = config['password'],
    sslmode = 'require',
    connect_timeout = 10
) as conn : 
    
    result = conn.execute(
        'create schema if not exists ch2;'  # ch2 : c드라이브, d드라이브 처럼 테이블을 모아 놓는 공간이라고 생각.
    )
    # 테이블 삭제 
    conn.execute('DROP TABLE if exists ch2.users')
    
    # 테이블 생성
    conn.execute(
    '''
        CREATE TABLE if not exists ch2.users(
            id bigint generated always as identity primary key,
            name text not null,
            email text not null unique
            );
    '''
    )
    print('테이블 준비 완료')

    # 사용자 2명 입력
    users = [
        ('이순신', 'esoonshin@korea.com'), ('윤봉길', 'yoonbongil@korea.com')
    ]
    with conn.cursor() as cur :
        cur.executemany('''
                        INSERT INTO ch2.users(name, email) VALUES(%s, %s)
                        ''', users
                        )
    print('사용자 저장 완료')

    # 전체 조회
    rows = conn.execute('''
        SELECT id, name, email FROM ch2.users ORDER BY id
        ''').fetchall() 
    for user_id, user_name, user_email in rows :
        print(user_id, user_name, user_email)

    # 수정
    conn.execute('''
        UPDATE ch2.users SET name = %s WHERE email = %s        
        ''', 
        ('강감찬', 'esoonshin@korea.com')
    )
    # 삭제
    conn.execute('DELETE FROM ch2.users WHERE email = %s;', ('esoonshin@korea.com',))


    # 전체 조회
    print('-------------- 변경 후 전체 조회')
    rows = conn.execute('''
        SELECT id, name, email FROM ch2.users ORDER BY id
        ''').fetchall() 
    for user_id, user_name, user_email in rows :
        print(user_id, user_name, user_email)



print('접속 종료')


