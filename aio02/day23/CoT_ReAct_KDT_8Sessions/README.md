# 11월 18일 · CoT와 ReAct 8차시

course.html 또는 course.pdf를 연다.

압축을 풀고 이 파일이 있는 폴더에서 실행한다. Python 3.11 이상을 사용한다.

Windows PowerShell
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe lesson.py
```

macOS / Linux
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python lesson.py
```

API 실습은 .env.example을 .env로 복사하고 선택한 공급자의 API_KEY와 MODEL을 채운다. 위 실행 명령 끝에 --provider groq, --provider gemini 또는 --provider openai 중 하나를 붙인다. Groq·Gemini는 수업 계정에서 무료 한도가 확인된 모델을 사용한다. OpenAI는 유료 선택 실습이다.


가상환경 Python으로 다음 파일을 실행한다. Windows에서 활성화하지 않았으면 python 대신 .\.venv\Scripts\python.exe를 사용한다.

| 차시 | 내용 | 실행 |
|---|---|---|
| 1 | 같은 문제에 CoT와 ReAct 적용하기 | `python lesson.py` |
| 2 | 같은 질문에 두 가지 지시문 작성하기 | `python s02.py` |
| 3 | 생성형 AI API로 풀이 비교하기 | `python s03.py` |
| 4 | 계산 요청을 파이썬 함수에 연결하기 | `python s04.py` |
| 5 | 도구의 반환값으로 다음 행동 결정하기 | `python s05.py` |
| 6 | 같은 조건에서 세 방식 비교하기 | `python s06.py` |
| 7 | 응답 오류와 반복 중단 재현하기 | `python s07.py` |
| 8 | 실행 기록으로 비교 보고서 만들기 | `python s08.py` |

API 모드는 1·3·5·6차시에서 선택한다. 1차시 결과와 6·8차시 비교 기록은 results/에 저장되며 나머지 차시의 출력은 터미널에 표시된다.
