import json
from pathlib import Path
from getpass import getpass

import psycopg  # 설치:pip install "psycopg[binary]" / 제거:python -m pip uninstall pycopg

config_path = Path(__file__).with_name('config.json')
print(config_path)
config = json.loads(config_path.read_text(encoding='utf-8')) # 
print(config)

# superbase 플랫폼의 database 접속 
# "https://supabase.com/ 에서 실습"


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
        'SELECT current_database(), current_user ;'
    ).fetchone()

print('접속 성공')
print(f'데이터베이스 : {result[0]}')
print(f'사용자 : {result[1]}')
