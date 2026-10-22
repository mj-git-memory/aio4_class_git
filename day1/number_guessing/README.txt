숫자 맞추기 게임 — 모듈 분리 실습

브라우저에서 실행 (권장)
  index.html을 더블 클릭하거나 브라우저로 열어 주세요.
  HTML, CSS, JavaScript를 하나의 파일에 담았습니다.
  Python 실행, 서버 실행, 패키지 설치 또는 인터넷 연결이 필요 없습니다.
  화면의 입력칸에 숫자를 입력하고 Enter 또는 확인하기를 누르세요.
  시도 기록과 남은 기회가 화면에 표시됩니다.
  새 게임 시작 버튼으로 새로운 정답을 생성할 수 있습니다.
  잘못된 입력은 시도 횟수에 포함하지 않습니다.
  10번 실패하면 정답을 공개합니다.
  기존 Python 파일을 호출하는 대신 같은 게임 규칙을 JavaScript로 구현했습니다.

파일 역할
  index.html : 브라우저 화면과 게임 동작. 단독 실행 가능합니다.
  main.py : 실행 시작점. game.py에서 play_game을 가져와 호출합니다.
  game.py : 난수 생성, 입력, 비교, 시도 횟수 관리와 반복 종료를 담당합니다.

실행 방법 (Python 3 필요, 별도 패키지 설치 불필요)
  aio_mj 폴더에서:
    python number_guessing/main.py

  또는 number_guessing 폴더에서:
    python main.py

Windows에서 Python 실행 명령이 py인 경우 python 대신 py를 사용하세요.

현재 컴퓨터의 번들 Python으로 실행하는 PowerShell 명령:
  & "C:\Users\Playdata\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\number_guessing\main.py
  위 명령은 aio_mj 폴더에서 실행합니다.

게임 방법
  1~100 사이의 정수를 입력하세요.
  입력한 값이 정답보다 큰지 작은지 안내합니다.
  정답을 맞히면 종료되며 최대 10번 시도할 수 있습니다.
  입력은 정수라고 가정합니다. 정수 이외의 문자열은 변환 오류가 납니다.

모듈 분리에서 사용한 문법
  def play_game(): 게임 코드를 함수로 묶습니다.
  from game import play_game: 다른 파일의 함수를 가져옵니다.
  if __name__ == "__main__": main.py를 직접 실행할 때만 게임을 시작합니다.
  game.py를 import하는 것만으로는 게임이 시작되지 않습니다.

원본 day1-5.py는 그대로 보존했습니다.
정답 범위, 최대 시도 횟수, 비교 안내와 정답 출력은 원본과 같습니다.
10번 모두 틀리면 원본처럼 추가 안내 없이 종료됩니다.
