
### 윈도우 버전 가상 환경 셋팅 명령어
# cd /d "C:\AI4\lesson_01_swagger"
# py -3.12 -m venv .venv
# .venv\Scripts\activate.bat
# python -m pip install -r requirements.txt
# python --version


### 맥 버전 가상 환경 셋팅 명령어
# cd "/Users/사용자이름/AI4/lesson_01_swagger" -> cd "day8/lesson_01_swagger"
# python3.12 -m venv .venv
# source .venv/bin/activate
# python -m pip install -r requirements.txt
# python --version

### 가상 서버 실행 
# cd "day8/lesson_01_swagger"
# python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
