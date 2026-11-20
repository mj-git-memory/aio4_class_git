# U2-03 실행 안내

ZIP을 풀고 main.py가 있는 폴더에서 Python 3.11 이상을 사용합니다.

```text
python -m venv .venv
```

Windows CMD는 `.venv\Scripts\activate.bat`, PowerShell은 `.\.venv\Scripts\Activate.ps1`, macOS·Linux는 `source .venv/bin/activate`로 활성화합니다.

```text
python -m pip install -r requirements.txt
```

현재 터미널에서 사용할 공급자의 키를 설정합니다. 예시는 Windows CMD 명령입니다. PowerShell에서는 `$env:GROQ_API_KEY='발급키'`, bash에서는 `export GROQ_API_KEY='발급키'` 형식을 사용합니다.

```cmd
set "GROQ_API_KEY=발급키"
set "GEMINI_API_KEY=발급키"
set "OPENAI_API_KEY=발급키"
```

기본은 Groq입니다. 계정에서 사용 가능한 구조화 출력 지원 모델로 바꾸려면 GROQ_MODEL, GEMINI_MODEL, OPENAI_MODEL을 설정합니다. Groq/Gemini에서 HTTP 429가 발생하면 같은 요청을 유료 OpenAI로 한 번 전환합니다. 5차시 chain은 OpenAI 전용입니다. 401/403은 키·권한, 400/404는 모델명·스키마 호환성을 확인합니다.

### 1차시 · CSV 한 행에서 응답 계약 찾기

```text
python main.py inspect --row 1
python main.py inspect --row 2
```

### 2차시 · 키의 존재와 값의 타입 설계하기

```text
python main.py schema
python main.py diagnose
```

### 3차시 · 프롬프트만 사용한 응답 측정하기

```text
python main.py plain --provider groq --row 1
python main.py plain --provider groq --row 2
```

### 4차시 · API 요청에 JSON Schema 전달하기

```text
python main.py strict --provider groq --row 1
python main.py strict --provider groq --row 2
```

### 5차시 · LangChain에서 Pydantic 객체 받기

```text
python main.py strict --provider openai --row 2
python main.py chain --provider openai --row 2
```

### 6차시 · 형식 오류와 원본 불일치 진단하기

```text
python main.py diagnose --row 1
python main.py diagnose --row 2
```

### 7차시 · 호출 중단과 한도 초과 처리하기

```text
python main.py strict --provider gemini --row 2
python main.py strict --provider groq --row 2
```

### 8차시 · 공개 데이터 원본과 응답 대조하기

```text
python main.py strict --row 1
python main.py strict --row 2
```

실행 기록은 runs/*.json 및 runs/*.html입니다. HTML을 열고 Ctrl+P → PDF로 저장합니다. evidence/에는 제작 시 실행한 로컬 검증 기록이 있습니다.
