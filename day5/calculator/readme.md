# 두 숫자 계산기

숫자 두 개를 입력하면 더하기·빼기·곱하기·나누기 결과를 한 번에 보여주는 로컬 웹 앱입니다.

## 사용하는 기술

| 기술 | 역할 |
| --- | --- |
| Python / FastAPI | 입력값을 검사하고 사칙연산을 수행하는 백엔드 |
| Uvicorn | 브라우저 요청을 받아 FastAPI 앱에 전달하는 서버 프로그램 |
| HTML | 입력창·버튼·결과 카드의 구조 |
| CSS | 색상·배치·작은 화면에 맞는 디자인 |
| JavaScript | 입력값을 API에 보내고, 응답 결과를 화면에 표시 |

DB나 외부 서비스는 사용하지 않습니다. 입력값과 결과를 저장하지 않습니다.

## 파일 구성

```text
calculator/
├── main.py             # API, 계산 로직, 화면/정적 파일 제공
├── requirements.txt    # 실행에 필요한 패키지
├── test_main.py        # API 자동 테스트
├── readme.md           # 이 안내서
└── static/
    ├── index.html      # 화면 구조
    ├── style.css       # 화면 디자인
    └── app.js          # 버튼, API 요청, 결과 표시
```

## 실행 방법: Mac + 기존 .venv

프로젝트 최상위 `AIO_4_class`에서 새 터미널을 열고 다음 명령을 차례로 실행합니다.

```bash
source .venv/bin/activate
cd day5/calculator
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

이미 `day5` 폴더에 있다면 다음을 사용합니다.

```bash
source ../.venv/bin/activate
cd calculator
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

이미 `.venv`가 활성화되어 있다면 활성화 명령은 생략해도 됩니다. `py313`을 사용하려면 해당 환경에서 `conda activate py313` 후 패키지를 설치하고 실행해도 됩니다.

브라우저에서 **http://127.0.0.1:8000** 을 엽니다. `index.html`을 파일로 직접 여는 대신 서버 주소로 접속하세요.

- API 설명/실행 화면: http://127.0.0.1:8000/docs
- 서버 종료: 서버 실행 터미널에서 `Ctrl + C`
- `Address already in use`가 나오면 기존 실습 서버를 종료하거나 다음 명령으로 포트를 바꾸세요.

```bash
python -m uvicorn main:app --reload --port 8001
```

이때 접속 주소는 **http://127.0.0.1:8001** 입니다.

### 아직 .venv가 없다면

`AIO_4_class`에서 Python 3.13 환경을 선택한 뒤 생성합니다. 기존 환경이 있다면 다시 만들 필요 없습니다.

```bash
conda activate py313
python -m venv .venv
source .venv/bin/activate
```

### 실행 명령 읽기

```bash
python -m uvicorn main:app --reload
```

- `python`: 현재 활성화된 환경의 파이썬
- `-m uvicorn`: 그 파이썬으로 Uvicorn 모듈 실행
- `main:app`: 현재 폴더의 `main.py` 안에 있는 `app` 사용
- `--reload`: 파일을 수정하고 저장하면 개발 서버 자동 재시작

이 안내에서는 반드시 `day5/calculator`로 이동한 뒤 실행합니다. `day4/main.py` 등 다른 파일과 혼동하지 않도록 합니다.

## 사용 방법과 예시

1. 첫 번째 숫자에 `12`, 두 번째 숫자에 `4`를 입력합니다.
2. **계산하기**를 누르거나 Enter를 누릅니다.
3. 더하기 `16`, 빼기 `8`, 곱하기 `48`, 나누기 `3`을 확인합니다.
4. **초기화**를 누르면 입력과 결과가 비워집니다.

| 입력 | 확인할 결과 |
| --- | --- |
| `-3`, `2` | 합 -1, 차 -5, 곱 -6, 몫 -1.5 |
| `0.1`, `0.2` | 합 0.3 (일반적인 부동소수점 오차 방지) |
| `1`, `3` | 몫 0.3333333333 |
| `2`, `3` | 몫 0.6666666667 |
| `7`, `0` | 합 7, 차 7, 곱 0, 나눗셈은 “0으로는 나눌 수 없어요.” |

빈 입력, 문자, 잘못된 숫자는 화면에서 안내합니다. 쉼표나 지수 표기 없이 `1234.5`, `-3` 같은 형태로 입력하세요. 숫자를 수정하면 이전 결과를 지우므로 다시 계산해 주세요.

## 요청이 처리되는 과정

```text
숫자 입력 → 계산하기 클릭
→ JavaScript가 POST /api/calculate 요청
→ FastAPI가 숫자의 형식과 범위 검사
→ Python의 Decimal로 계산
→ JSON 응답
→ JavaScript가 결과 카드 갱신
```

프론트엔드는 화면을 담당하고, 실제 연산은 서버에서 합니다. 브라우저의 숫자 정밀도 손실을 피하려고 요청의 숫자는 문자열로 전달합니다.

### API 예시

`POST /api/calculate`

요청:

```json
{"a": "12", "b": "4"}
```

성공 응답 (`200 OK`):

```json
{
  "a": "12",
  "b": "4",
  "addition": "16",
  "subtraction": "8",
  "multiplication": "48",
  "division": "3",
  "division_error": null
}
```

응답의 숫자도 정확한 표시를 위해 문자열로 보냅니다. 나누는 수가 0이면 `division`은 `null`, `division_error`에는 안내 문구가 들어갑니다. 다른 세 연산은 정상 계산하므로 전체 요청은 200입니다. 입력 자체가 잘못되면 API는 422를 반환합니다.

## 계산 규칙

- 정수·음수·소수 허용. 입력은 각 숫자당 최대 유효 숫자 30자리, 소수점 아래 10자리이며, Pydantic의 Decimal 제약에 따라 정수 부분은 최대 20자리입니다.
- 더하기·빼기·곱하기는 Decimal로 계산합니다.
- 나눗셈만 소수점 아래 10자리까지 반올림합니다. 정확히 절반이면 절댓값이 커지는 방향으로 반올림합니다.
- 결과의 불필요한 소수점 뒤 0과 음수 0은 제거합니다.
- NaN·무한대·빈 값·잘못된 숫자·범위를 벗어난 입력은 거절합니다.

## 검증 및 한계

기존 Python 3.13 가상환경에서 자동 테스트 **18개가 통과**했습니다. 정수·음수·소수, 반복소수 반올림, 큰 수 곱셈, 0으로 나누기, 잘못된 입력과 HTML/CSS/JS 제공을 검증했습니다.

테스트를 다시 실행하려면 `day5/calculator`에서:

```bash
python -m pip install pytest httpx
python -m pytest -q
```

JavaScript 문법 검사도 통과했고, Uvicorn 서버에 실제 HTTP 요청을 보내 `12`, `4`의 계산 결과를 확인했습니다.

JavaScript 문법을 다시 검사하려면 Node.js가 있을 때 `node --check static/app.js`로 확인할 수 있습니다.

검증 시점에 브라우저 자동 제어 연결을 사용할 수 없어 실제 브라우저의 화면 배치와 클릭 동작은 자동 확인하지 못했습니다. 화면에서 `12`와 `4` 계산, `7`과 `0` 계산, 초기화 버튼을 직접 확인할 수 있습니다.

테스트 도구에서 httpx 관련 폐기 예정 경고가 나올 수 있으나 테스트 실패는 아닙니다. 실행용 패키지는 `requirements.txt`에 분리했습니다.
