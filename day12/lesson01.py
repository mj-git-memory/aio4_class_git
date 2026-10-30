import os
from dotenv import load_dotenv # python3 -m pip install python-dotenv

# .env 읽어옴
load_dotenv()

# 환경변수 읽어오기
print(os.getenv('host'))
print(os.getenv('port'))
print(os.getenv('dbname'))
print(os.getenv('user'))
print(os.getenv('password'))
