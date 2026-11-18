# Git·GitHub 학습 정리 (10.19)

Oct 19, 2026 · @Mijeong Lee

오늘은 맥에서 Git·GitHub 환경을 처음부터 세팅하고, 저장소 2개(aio4\_class → 삭제, aio4\_class\_git)로 add·commit·push·pull·clone·branch·PR merge까지 한 바퀴 돌았어. 아래는 그 과정에서 묻고 답한 내용을 흐름 순서대로 정리한 거야.

질문과 답변 원문 정리: Q&A 목록

## 0. 오늘 한 일 한눈에 보기

| 순서 | 한 일 | 결과 |
| --- | --- | --- |
| 1 | VS Code 업데이트 오류 해결 | 앱을 응용 프로그램 폴더로 옮겨서 해결, 데스크탑 중복 앱 삭제 |
| 2 | VS Code에 Codex 확장 설치 | 로그인 → 폴더 열기 → 사이드바 패널에서 사용 |
| 3 | Homebrew → Git 설치 | `brew install git` 완료 |
| 4 | aio4\_class 저장소에 첫 push | askpass 오류, 작성자 미설정 → VS Code 재시작, `--amend` + 강제 push |
| 5 | 나머지 파일 push, .DS\_Store 제거 | `.gitignore` 추가 + `git rm --cached` |
| 6 | aio4\_class 삭제 → aio4\_class\_git 새로 만들기 | 로컬 `.git` 삭제 후 day4만 다시 push |
| 7 | GitHub 웹에서 README 수정 → 로컬로 pull | 로컬 수정과 겹쳐 stash → 충돌 → 정리 후 push |
| 8 | AIO\_4\_practice 폴더에 clone | 빈 폴더가 아니라서 실패 → `.gitignore` 옮기고 clone |
| 9 | feature/login, feature/backend 브랜치 | 브랜치 생성 → push → GitHub PR로 main에 merge |
| 10 | AIO\_4\_class에서 깃 내용 복습.md push | rejected (fetch first) → git pull --no-edit 후 push |
| 11 | day4/main.py 로컬·GitHub 삭제 | git rm → commit → push |

## 1. 개발 환경 준비 Q&A

### VS Code 업데이트 오류: Cannot update while running on a read-only volume

- **원인:** VS Code를 다운로드 폴더에서 바로 실행해서. macOS는 다운로드 폴더 앱을 임시 읽기 전용 위치로 옮겨 실행(App Translocation)해서 업데이트 파일을 덮어쓸 수 없어.
- **해결:** `Cmd + Q`로 종료 → Finder에서 앱을 **응용 프로그램(Applications)** 폴더로 드래그 → 거기서 다시 실행 → 업데이트.
- 그래도 안 되면 격리 속성 제거: `xattr -dr com.apple.quarantine "/Applications/Visual Studio Code.app"`

### 검색하면 VS Code가 두 개 뜨는 이유

- 응용 프로그램 폴더와 데스크탑에 **복사본이 하나씩** 있었던 거야.
- 응용 프로그램 것만 남기고 데스크탑 것은 삭제. 확장·설정은 `~/Library/Application Support/Code`, `~/.vscode`에 있어서 앱을 지워도 그대로 남아.
- Dock 아이콘이 지운 쪽을 가리키면 물음표가 뜨니, 응용 프로그램에서 실행 후 `옵션 → Dock에 유지`로 다시 고정.

### VS Code에서 Codex 사용법

1. 사이드바 Codex 아이콘 → 브라우저에서 OpenAI 계정 로그인 (유료 ChatGPT 구독 필요)
2. `File → Open Folder`로 작업 폴더 열기
3. 실행 환경: 로컬(Work locally) 또는 클라우드(Run in the cloud)
4. 권한 모드: **Chat**(읽기 전용) / **Agent**(수정 전 승인 요청, 기본값) / **Agent Full Access**(묻지 않고 실행)
5. 패널에 자연어로 요청 → Agent 모드에선 diff 확인 후 승인

### Homebrew → Git 설치

1. Homebrew 설치 명령 실행 → 비밀번호 입력(화면에 안 보이는 게 정상) → `Press RETURN/ENTER to continue` 나오면 **Enter**
2. 끝나면 `Next steps`의 PATH 설정 명령을 꼭 실행: `eval "$(/opt/homebrew/bin/brew shellenv)"` 를 `~/.zprofile`에 추가
3. `brew --version`으로 확인 → `brew install git` → `Do you want to proceed? [y/n]`에 **y** (git + 보조 라이브러리 4개 설치 확인 질문)
4. `git --version` 확인

- 명령어는 **한 줄씩** 입력하는 게 안전해. 여러 줄을 붙여넣으면 다음 줄이 y/n 질문의 답으로 들어갈 수 있어.
- bash 터미널에선 Apple 기본 git(2.50.1)이 잡히고, zsh에선 Homebrew git(2.56)이 잡혀. PATH 설정을 zsh용 `~/.zprofile`에만 넣었기 때문이야. 앞으로 **zsh 터미널** 사용 추천.

### .DS\_Store와 숨김 파일

- `.DS_Store`는 git과 무관하게 **Finder가 폴더마다 자동으로 만드는 보기 설정 파일**이야. 올릴 필요 없어서 `.gitignore`에 넣어.
- 이름이 `.`으로 시작하면 맥에선 숨김 파일이라 안 보여(`.gitignore`, `.git`도 마찬가지).
- **보이게 하기:** Finder에서 `Cmd + Shift + .` (한 번 더 누르면 숨김), 터미널에선 `ls -a`
- `.git` 폴더는 모든 기록이 들어 있으니 건드리지 않기.

## 2. 핵심 개념

### 로컬 저장소 vs 원격 저장소

- **로컬 저장소:** 내 컴퓨터 폴더 + 그 안의 `.git` 폴더. 커밋 기록(Graph)은 전부 여기 저장돼.
- **원격 저장소:** GitHub에 있는 저장소. push로 올리고 pull로 받아.
- 둘은 **자동으로 동기화되지 않아.** GitHub 저장소를 지워도 로컬 `.git`과 Graph 기록은 그대로 남아 (aio4\_class 삭제 후 Graph가 남아 있던 이유).

### origin vs main

|  | origin | main |
| --- | --- | --- |
| 정체 | 원격 **저장소** 이름(별칭) | **브랜치** 이름 |
| 가리키는 것 | `https://github.com/mj-git-memory/aio4_class_git.git` | 저장소 안의 작업 줄기 하나 |
| 질문 | "**어디** 저장소?" | "그 저장소의 **어느** 줄기?" |

- 비유: origin = 건물 주소, main·feature/backend = 그 건물 안의 방.
- `git push origin feature/backend` = "origin 건물의 feature/backend 방으로 보내라".
- origin은 관례적인 이름일 뿐이라 다른 이름도 가능해. `git clone`하면 자동으로 origin이 붙어.
- 연결은 **폴더(저장소)마다 따로**야. AIO\_4\_class와 AIO\_4\_practice 둘 다 같은 URL에 연결할 수 있지만, 서로는 GitHub를 거쳐서만 동기화돼.

### main / origin/main / origin

```
main         → 내 컴퓨터의 main 브랜치
origin/main  → GitHub(origin)의 main 브랜치를 내 컴퓨터가 마지막으로 확인한 상태
origin       → GitHub 저장소 자체
```

### upstream (짝꿍)

- 로컬 브랜치와 짝을 이루는 원격 브랜치. 예: 로컬 `feature/backend` ↔ `origin/feature/backend`
- 짝을 정해두면 `git push`, `git pull`만 쳐도 어디로 보내고 받을지 git이 알아.
- `git status`의 `Your branch is up to date with 'origin/main'`이 짝이 있다는 표시.
- 짝 정하는 법: 처음 push할 때 `-u` (= `--set-upstream`). clone한 main, 원격에 이미 있는 브랜치로 switch하면 자동으로 짝이 정해져.

### 브랜치

- 작업 줄기. main에서 갈라져 나와 독립적으로 커밋이 쌓여.
- feature/login에 커밋해도 main엔 영향 없음. `git switch`로 옮기면 폴더 파일도 그 브랜치 상태로 바뀌어.
- **갈라진 시점이 중요:** feature/backend는 PR #1 merge 전 main에서 만들어서, 그 뒤 main에 들어온 `git_practice.py`가 없었어.

### VS Code Graph 읽는 법

- 아래 → 위 순서로 오래된 커밋 → 최신 커밋.
- `main` 배지 = 내 위치, 구름 아이콘 `origin/main` = GitHub 위치.
- 두 배지가 같은 커밋에 붙어 있으면 → 로컬 = GitHub
- `main`이 위 → **Outgoing Changes** (내가 아직 push 안 한 커밋 있음 → push)
- `origin/main`이 위 → **Incoming Changes** (GitHub에 아직 pull 안 한 커밋 있음 → pull)
- 줄이 갈라졌다 합쳐지는 모양 = 브랜치가 갈라졌다가 merge된 것.

### 파일 상태 표시 (Source Control)

| 표시 | 의미 |
| --- | --- |
| U | Untracked: git이 아직 관리 안 하는 새 파일 |
| A | Added: 새로 추가돼 커밋에 들어가는 파일 |
| M | Modified: 수정된 파일 |
| D | Deleted: 삭제된 파일 |
| ↓M | GitHub에서 받을 변경이 있는 파일 |

## 3. 작업 흐름 순서대로

택배로 비유하면: `init` 창고 만들기 → `add` 상자에 담기 → `commit` 봉인하고 송장 붙이기(내 컴퓨터에만) → `push` 발송 → `pull` 도착한 택배 받기.

### 3-1. 최초 1회: 사용자 정보 설정

```bash
git config --global user.name "mjlee"
git config --global user.email "GitHub에 등록한 이메일"
git config --global init.defaultBranch main
```

- 이메일이 GitHub 계정 이메일이어야 잔디(contribution)에 기록돼.
- 설정 전에 커밋했다면 `git commit --amend --reset-author --no-edit`로 작성자를 고쳐 (push 전이면 안전).

### 3-2. GitHub 저장소 생성

1. GitHub `+ → New repository` → 이름 입력 → Public/Private → **Create repository**
2. 로컬 프로젝트를 올릴 거면 README·.gitignore·license 체크 없이 **빈 저장소**로 만드는 게 간단해.
3. HTTPS 주소 복사.

### 3-3. 방법 A: 로컬 폴더를 새로 연결 (init)

```bash
git init
git add .
git status
git commit -m "first commit"
git remote add origin https://github.com/mj-git-memory/aio4_class_git.git
git push -u origin main
```

- 특정 파일·폴더만 올리기: `git add day4/ README.md .gitignore`
- 잘못 담았으면 `git reset` (담은 것만 취소, 파일은 그대로)
- 첫 push 때 VS Code 팝업으로 GitHub 로그인. 터미널에 Username/Password 직접 입력은 안 돼(비밀번호 로그인 막힘).

### 3-4. 방법 B: GitHub 저장소를 내려받기 (clone)

```bash
git clone https://github.com/mj-git-memory/aio4_class_git .
```

- 끝의 `.` = 지금 폴더에 받기. **폴더가 비어 있어야** 해.
- `.` 없이 하면 `aio4_class_git` 하위 폴더가 새로 생기면서 거기로 받아져 → `cd aio4_class_git`
- clone하면 origin 연결 + main 짝(upstream)까지 자동 설정. 바로 `git push`, `git pull` 가능.

### 3-5. 평소 반복 작업

```bash
git pull                      # 1. 작업 시작 전 항상 최신 받기
# 파일 수정, 저장
git status                    # 2. 상태 확인
git add .                     # 3. 담기
git commit -m "무엇을 했는지"   # 4. 커밋
git push                      # 5. 올리기
```

- VS Code의 **Commit & Push** 버튼 = add → commit → push를 한 번에.
- 두 폴더(AIO\_4\_class, AIO\_4\_practice)에서 같은 저장소를 쓰면 폴더를 옮길 때마다 pull부터.

### 3-6. 올리면 안 되는 파일 관리 (.gitignore)

```
.DS_Store
.vscode
.env
*.pdf
__pycache__/
*.pyc
.ipynb_checkpoints/
day1/
```

- `.gitignore`는 **아직 관리 안 되는 파일**에만 효과가 있어.
- 이미 커밋된 파일 빼기: `git rm --cached '*.DS_Store'` → `.gitignore` 저장 → commit → push

### 3-7. 브랜치 만들고 작업하기

```bash
git switch -c feature/login        # 만들고 이동
git branch                         # 목록 확인 (* = 현재 브랜치)
# 작업, 저장
git add .
git commit -m "로그인 기능 추가"
git push -u origin feature/login   # 새 브랜치 첫 push만 -u
```

- 이미 원격에 있는 브랜치로 이동: `git switch feature/backend` → 이후 `git push`만
- 브랜치에 main 최신 내용 반영: 그 브랜치에서 `git pull origin main`
- VS Code: 왼쪽 아래 브랜치 이름 클릭 → Create new branch / 브랜치 이동

### 3-8. main에 합치기 (merge)

**A. GitHub Pull Request (실무 방식)**

1. 저장소 페이지 `Compare & pull request` (또는 Pull requests → New pull request)
2. **base: main ← compare: feature/login** 확인, `Able to merge` 확인
3. 제목 입력 → **Create pull request** (요청만 올린 상태)
4. **Merge pull request** → **Confirm merge** (여기서 실제로 합쳐짐)
5. 필요하면 **Delete branch**
6. 로컬 반영: `git switch main` → `git pull`

**B. 로컬에서 바로 합치기 (혼자 쓸 때)**

```bash
git switch main
git merge feature/login
git push
```

**실무에서 PR을 쓰는 이유:** 코드 리뷰·승인, 변경 이유와 논의 기록, 자동 테스트(CI), main 직접 push 금지(branch protection), 합치기 전 충돌 확인. 혼자 연습이면 B도 OK지만 PR로 연습해두면 협업 때 바로 익숙해.

### 3-9. 정리: 삭제·변경

| 하고 싶은 것 | 명령어 |
| --- | --- |
| 로컬 브랜치 삭제 | `git branch -d feature/login` |
| GitHub 브랜치 삭제 | `git push origin --delete feature/login` 또는 PR의 Delete branch |
| 원격 주소만 변경 | `git remote set-url origin 새URL` |
| 원격 연결 해제 | `git remote remove origin` |
| GitHub 저장소 삭제 | 저장소 Settings → 맨 아래 Danger Zone → Delete this repository |
| 로컬 git 기록 전부 삭제 후 새로 시작 | `rm -rf .git` → `git init` (파일은 남고 기록만 사라짐, 되돌릴 수 없음) |
| 파일을 로컬·GitHub에서 삭제 | git rm day4/main.py → commit → push |
| GitHub에서만 빼고 로컬 유지 | git rm --cached day4/main.py → commit → push |

- GitHub 저장소를 지우고 새로 만들었으면, 로컬은 `set-url`로 주소만 바꾸면 기록 유지 / `rm -rf .git`이면 기록 없이 새 출발.
- rm :	파일이나 폴더 삭제
- -r :	폴더 안의 내용까지 모두 삭제
- -f :	일반적인 확인 질문 없이 강제로 삭제
- .git :	Git 이력과 설정을 저장하는 숨김 폴더

## 4. 명령어 사전

### 4-0. 명령어·옵션 한눈에 보기

**git 명령어 (뭐 하는 함수?)**

| 명령어 | 하는 일 | 내 폴더 기준 예시 |
| --- | --- | --- |
| `git init` | 지금 폴더를 git 저장소로 만듦 (`.git` 생성) | `AIO_4_class`에서 `git init` |
| `git status` | 현재 브랜치, 짝과의 차이, 담긴/안 담긴 파일 확인 | `git status` |
| `git add` | 커밋할 파일을 담기(스테이징) | `git add day4/day4.py` |
| `git commit` | 담은 파일을 하나의 버전으로 로컬에 저장 | `git commit -m "day4 실습 추가"` |
| `git push` | 내 커밋을 GitHub로 올리기 | `git push` |
| `git pull` | GitHub 변경을 받아서 지금 브랜치에 합치기 | `git pull` |
| `git clone` | GitHub 저장소를 통째로 내려받기 (+ origin 연결, 짝 설정) | `git clone https://github.com/mj-git-memory/aio4_class_git .` |
| `git remote` | 원격 저장소 주소록 관리 | `git remote -v` |
| `git branch` | 브랜치 목록 보기·이름 변경·삭제 | `git branch -d feature/login` |
| `git switch` | 브랜치 이동 (`-c`로 생성+이동) | `git switch feature/backend` |
| `git merge` | 다른 브랜치를 지금 브랜치에 합치기 | `git merge feature/login` |
| `git stash` | 커밋 안 한 수정을 잠깐 보관(서랍) | `git stash` → `git stash pop` |
| `git rm` | 파일을 삭제하고 "삭제됨"을 커밋 대상으로 담기 | `git rm day4/main.py` |
| `git restore` | 커밋 안 한 수정을 버리고 마지막 커밋 상태로 되돌리기 | `git restore README.md` |
| `git reset` | add로 담은 것 취소 (파일 내용은 그대로) | `git reset` |
| `git config` | 이름·이메일 등 git 설정 | `git config --global user.name "mj-git-memory"` |
| `git log` | 커밋 기록 보기 | `git log --oneline -1` |

**하위 명령어(서브커맨드)**

| 쓰는 곳 | 하위 명령어 | 하는 일 |
| --- | --- | --- |
| `git remote` | `add` | 원격 저장소를 이름 붙여 등록 |
| `git remote` | `set-url` | 등록된 원격의 주소만 바꾸기 |
| `git remote` | `remove` | 원격 등록 해제 (GitHub 저장소는 그대로) |
| `git stash` | `pop` | 서랍에서 꺼내 다시 얹고 서랍에서 지움 (충돌 나면 남음) |
| `git stash` | `list` | 서랍 목록 |
| `git stash` | `drop` | 서랍에서 지우기 |
| `git stash` | `push -u -m "메모"` | 새 파일까지 포함해 메모와 함께 보관 |

**옵션 (`-` 하나는 줄임, `--` 두 개는 풀네임)**

| 옵션 | 풀네임/뜻 | 쓰는 곳 | 하는 일 |
| --- | --- | --- | --- |
| `-m` | message | `git commit -m "메시지"` | 커밋 메시지를 바로 적기 (없으면 편집기가 열림) |
| `-u` | `--set-upstream` | `git push -u origin main` | 로컬 브랜치와 원격 브랜치를 짝으로 연결. 업데이트 아님 |
| `-c` | create | `git switch -c feature/login` | 브랜치를 새로 만들고 바로 이동 |
| `-M` | move(force) | `git branch -M main` | 현재 브랜치 이름을 강제로 바꾸기 |
| `-d` | delete | `git branch -d feature/login` | 이미 합쳐진 브랜치 삭제 (안 합쳐졌으면 거부, 강제는 `-D`) |
| `-v` | verbose | `git remote -v` | 이름과 주소까지 자세히 보기 |
| `-r` | recursive | `git rm -r --cached day1/` | 폴더 안까지 전부 |
| `--cached` | 스테이징(인덱스)만 | `git rm --cached '*.DS_Store'` | 내 컴퓨터 파일은 두고 git 관리에서만 빼기 |
| `--global` | 전역 설정 | `git config --global ...` | 이 PC 계정의 모든 저장소에 적용 |
| `--get` | 값 읽기 | `git config --get user.name` | 설정값 확인 |
| `--amend` | 고치기 | `git commit --amend` | 마지막 커밋을 새 커밋으로 교체 |
| `--reset-author` | 작성자 재설정 | `git commit --amend --reset-author` | 커밋 작성자를 현재 설정으로 |
| `--no-edit` | 편집 없이 | `git commit --amend --no-edit`, `git pull --no-edit` | 메시지를 그대로/기본값으로 (편집기 안 열림) |
| `--force-with-lease` | 안전한 강제 | `git push --force-with-lease` | GitHub 기록을 내 기록으로 덮어쓰되 그사이 변경이 있으면 멈춤 |
| `--delete` | 삭제 | `git push origin --delete feature/backend` | GitHub의 브랜치 삭제 |
| `--rebase` | 재배치 | `git pull --rebase origin main` | 받은 커밋 위에 내 커밋을 다시 얹기 (merge 커밋 없이) |
| `--oneline` | 한 줄 | `git log --oneline` | 커밋을 한 줄씩 짧게 |
| `.` | 현재 폴더 | `git add .`, `git clone URL .` | 지금 폴더 전체 / 지금 폴더에 받기 |

**터미널 옵션**

| 명령 | 뜻 |
| --- | --- |
| `ls -a` | `-a` = all, 숨김 파일까지 목록 |
| `rm -rf .git` | `-r` 폴더 안까지, `-f` 확인 없이 강제 삭제 |
| `mkdir -p ~/AI4/ai4_lecture` | `-p` 중간 폴더까지 한 번에 만들기 |
| `grep -n -E '패턴' README.md` | `-n` 줄 번호, `-E` 정규식 사용 |
| `xattr -dr ...` | `-d` 속성 삭제, `-r` 하위 전부 |

### git init

지금 폴더를 git 저장소로 만들어. 숨김 폴더 `.git`이 생기고 여기에 모든 기록이 쌓여. 이미 저장소인 곳에서 다시 하면 `Reinitialized existing Git repository`가 뜨는데, 기록은 안 지워지니 무해해.

### git status

지금 상태 보기. 어느 브랜치인지, 짝(upstream)과 비교해 앞서거나 뒤처졌는지, 어떤 파일이 담겼고(초록) 안 담겼는지(빨강) 알려줘. 헷갈리면 일단 이것부터.

### git add

커밋할 파일을 골라 상자에 담기(스테이징).

```bash
git add README.md          # 파일 하나
git add day4/              # 폴더째
git add .                  # 현재 폴더의 모든 변경(.gitignore 대상 제외)
```

### git commit

담은 파일들을 메시지와 함께 하나의 버전으로 저장. **내 컴퓨터에만** 저장돼, push 전까진 GitHub에 없어.

```bash
git commit -m "메시지"
git commit --amend --reset-author --no-edit
#          고치기    작성자 새로 설정   메시지는 그대로
```

`--amend`는 커밋을 수정하는 게 아니라 **새 커밋으로 교체**하는 거라, 이미 push했다면 로컬과 GitHub 기록이 달라져서 강제 push가 필요해.

### git push

내 커밋들을 GitHub로 올리기.

```bash
git push -u origin main
#        짝 정하기  어디로  어느 브랜치
```

`-u`는 업데이트가 아니라 **upstream**이야. `--set-upstream`의 줄임말로, "이 로컬 브랜치의 짝꿍(upstream)을 origin의 main으로 정해둬라"는 뜻이야. 짝을 정해두면 그 브랜치에서는 `git push`, `git pull`만 쳐도 git이 알아서 origin/main으로 보내고 받아. **처음 한 번만** 쓰면 돼.

```bash
git push                         # 짝이 정해진 뒤엔 이것만
git push -u origin feature/login # 새 브랜치 첫 push
git push --force-with-lease      # 강제 push(안전 버전)
git push origin --delete 브랜치명  # GitHub 브랜치 삭제
```

`--force-with-lease`는 GitHub 기록을 내 기록으로 덮어쓰되, 그사이 GitHub에 다른 변경이 생겼으면 멈추는 안전한 강제 push야. 혼자 쓰는 저장소에서 내 커밋을 고친 직후에만 써.

### git pull

GitHub의 변경을 받아서 지금 브랜치에 합치기. push와 방향이 반대야.

|  | `git pull` | `git pull origin main` |
| --- | --- | --- |
| 의미 | 지금 브랜치의 **짝**에서 받기 | **origin의 main**에서 받아 지금 브랜치에 합치기 |
| 짝 필요 | 필요 | 필요 없음 |
| 언제 | 평소 대부분 | 짝이 없을 때, 다른 브랜치에서 main 최신 내용을 가져올 때 |

main에 있고 짝이 origin/main이면 둘은 같은 결과야. 내가 만든 커밋이 아직 GitHub에 없을 때 pull하면 `Already up to date`가 나오는데, 받을 게 없다는 뜻이지 올라갔다는 뜻이 아니야(올리는 건 push).

### git clone

GitHub 저장소를 통째로 내려받기 + origin 연결 + main 짝 설정까지 한 번에.

```bash
git clone URL      # URL 이름의 하위 폴더를 만들어 받기
git clone URL .    # 지금 폴더에 바로 받기(빈 폴더여야 함)
```

**clone(복제) 문법**

```bash
git clone <저장소 URL> [받을 폴더 이름]
#         필수          선택 (없으면 저장소 이름으로 새 폴더)
```

**예시 (내 폴더 기준)**

```bash
# 1. Downloads에서 하위 폴더로 받기 → ~/Downloads/aio4_class_git 생성
cd ~/Downloads
git clone https://github.com/mj-git-memory/aio4_class_git
cd aio4_class_git

# 2. 원하는 폴더 이름으로 받기 → ~/Downloads/AIO_4_practice 생성
cd ~/Downloads
git clone https://github.com/mj-git-memory/aio4_class_git AIO_4_practice

# 3. 이미 만든 빈 폴더 안에 바로 받기 (폴더가 비어 있어야 함)
cd ~/Downloads/AIO_4_practice
git clone https://github.com/mj-git-memory/aio4_class_git .

# 4. 특정 브랜치로 받기
git clone -b feature/backend https://github.com/mj-git-memory/aio4_class_git
#         -b = branch, 받은 뒤 바로 그 브랜치에 있음
```

clone 뒤 확인: `git remote -v` (origin 자동 등록) → `git status` (`Your branch is up to date with 'origin/main'`, 짝 자동 설정). 바로 `git pull`, `git push`가 돼.

| clone | init + remote add |
| --- | --- |
| GitHub에 이미 파일이 있을 때 | 로컬에 파일이 있고 GitHub는 빈 저장소일 때 |
| 명령 한 줄로 받기 + 연결 + 짝 | `init` → `add` → `commit` → `remote add` → `push -u` |

### git remote

원격 저장소 주소록 관리. `git remote add origin URL` = "이 로컬 저장소에 이 URL을 origin이라는 이름으로 등록해라".

```bash
git remote -v                     # 등록된 원격 확인(fetch=받기, push=올리기 주소)
git remote add origin URL         # 새로 등록
git remote set-url origin 새URL   # 주소만 변경
git remote remove origin          # 등록 해제(GitHub 저장소는 그대로)
```

### git branch

브랜치 확인·이름 변경·삭제.

```bash
git branch                   # 목록(* = 현재)
git branch -M main           # 현재 브랜치 이름을 main으로 강제 변경
git branch -d feature/login  # 합쳐진 브랜치 삭제
```

### git switch

브랜치 이동. 예전 자료의 `git checkout`과 같은 뜻인데 브랜치 이동 전용으로 새로 나온 명령어야.

```bash
git switch main              # main으로 이동
git switch -c feature/login  # 새로 만들고(-c = create) 바로 이동
```

커밋 안 한 수정이 있으면 이동이 막힐 수 있으니 먼저 commit 해두기.

### git merge

다른 브랜치의 커밋을 지금 브랜치에 합치기. `git switch main` → `git merge feature/login` = feature/login을 main에 합쳐.

### git rm

파일을 git 관리에서 빼기.

```bash
git rm 파일명                # git에서도, 내 컴퓨터에서도 삭제
git rm --cached '*.DS_Store' # 내 컴퓨터 파일은 두고 git 기록에서만 빼기(하위 폴더까지)
```

로컬과 GitHub에서 파일 삭제 (예: `day4/main.py`):

```bash
git pull
git rm day4/main.py
git status                        # deleted: day4/main.py
git commit -m "day4/main.py 삭제"
git push
```

Finder/VS Code에서 이미 지웠다면 `git add day4/main.py`로 "삭제됨"을 담고 commit → push. GitHub에 안 올라간 `U` 파일(`day2/chat_filter/main.py` 등)은 그냥 지우면 끝.

### git restore / git reset

```bash
git restore README.md   # 커밋 안 한 수정을 버리고 마지막 커밋 상태로 되돌리기
git reset               # add로 담은 것 전부 취소(파일 내용은 그대로)
```

### git stash

커밋 안 한 수정을 잠깐 서랍에 넣어두기.

```bash
git stash        # 서랍에 넣기 → 작업 폴더가 깨끗해짐
git stash pop    # 서랍에서 꺼내 다시 얹기(충돌 나면 서랍에 남음)
git stash list   # 서랍 목록
git stash drop   # 서랍에서 지우기
```

### git config

```bash
git config --global user.name "이름"   # --global = 이 PC 계정 전체에 적용
git config --get user.name             # 설정값 확인
git config --global pull.rebase false  # pull 시 merge 방식으로 합치기
```

### 기타 터미널 명령어

| 명령어 | 의미 |
| --- | --- |
| `ls -a` | 숨김 파일까지 목록 보기 |
| `mv A B` | A를 B로 옮기기/이름 바꾸기 |
| `rm -rf .git` | `.git` 폴더 강제 삭제(git 기록 전부 삭제) |
| `cd 폴더` | 폴더 이동 |
| `Ctrl + C` | 실행 중인 명령/입력 대기 취소 |
| `grep -n 패턴 파일` | 파일에서 패턴이 있는 줄 번호와 함께 찾기 |

## 5. 오류 메시지 사전

| 오류 메시지 | 무슨 뜻이야? | 해결 |
| --- | --- | --- |
| `Reinitialized existing Git repository` | (오류 아님) 이미 git 저장소라 다시 초기화만 함 | 그대로 둬도 됨 |
| `nothing added to commit but untracked files present` | 담은(add) 파일이 없어 커밋 안 됨 | `git add` 먼저 |
| `Everything up-to-date` | push할 새 커밋이 없음 | commit 했는지 확인 |
| `Already up to date.` | pull로 받을 새 커밋이 없음 (올렸다는 뜻 아님) | 올릴 게 있으면 `git push` |
| `error: remote origin already exists.` | 이미 origin이 등록돼 있는데 또 add | `git remote set-url origin 새URL` |
| `error: Your local changes to the following files would be overwritten by merge` | 받으려는 파일에 내 커밋 안 한 수정이 있어 덮어쓸 위험 → pull 중단(Aborting) | 버릴 거면 `git restore 파일` / 살릴 거면 commit 또는 `stash → pull → stash pop` |
| `CONFLICT (content): Merge conflict in README.md` | 같은 부분을 양쪽에서 고쳐 자동으로 못 합침 | 파일의 충돌 표시 정리 → 저장 → add → commit |
| `both modified: README.md` | 충돌 난 파일 (Unmerged paths) | 위와 같음 |
| `The stash entry is kept in case you need it again` | 충돌이 나서 stash가 자동 삭제되지 않고 남음 | 정리 끝나면 `git stash drop` |
| `fatal: destination path '.' already exists and is not an empty directory` | clone은 빈 폴더에만 가능한데 `.gitignore`가 있었음 | 파일을 옮겨 폴더 비우고 clone, 또는 `.` 빼고 clone |
| `hint: You have divergent branches...` | 로컬·GitHub 양쪽에 서로 모르는 커밋이 있어 합치는 방식을 정해야 함 | `git config --global pull.rebase false` 후 pull |
| `rejected` / `non-fast-forward` | GitHub에 내가 받지 않은 커밋이 있음 (`--amend` 후에도 발생) | 보통 `pull` 후 push. 내 커밋을 고친 경우만 `--force-with-lease` |
| ! \[rejected\] main -> main (fetch first) / failed to push some refs | GitHub에 내 폴더엔 없는 커밋이 있음 (다른 폴더 AIO\_4\_practice에서 PR merge함) | git pull --no-edit 후 git push |

### 충돌 표시 읽는 법

```
<<<<<<< Updated upstream
(GitHub에서 받은 내용)
=======
(내가 stash 해뒀던 내용)
>>>>>>> Stashed changes
```

남길 내용만 두고 `<<<<<<<`, `=======`, `>>>>>>>` 세 줄을 지운 뒤 저장. VS Code에서는 Accept Current / Accept Incoming / Accept Both 버튼으로 골라도 돼. 남은 표시 확인: `grep -n -E '^(<<<<<<<|=======|>>>>>>>)' README.md` (아무것도 안 나오면 깨끗).

## 6. 오늘 겪은 상황별 해결 기록

### 사용자 설정 전에 push해버렸을 때

1. `git config --global user.name/email` 설정
2. `git commit --amend --reset-author --no-edit` → 로컬에 새 커밋(146b215)이 생겨 GitHub(2d6b3c4)와 달라짐
3. `git push --force-with-lease` → `+ 2d6b3c4...146b215 main -> main (forced update)` = GitHub 쪽 커밋을 새 작성자로 교체

강제 push는 혼자 쓰는 저장소에서 내 커밋을 고친 직후에만. 공용 저장소에선 남의 작업을 날릴 수 있어.

### README만 올라가고 나머지는 안 올라갔을 때

처음에 `git add README.md`로 README만 담았기 때문. 나머지 파일은 `U`(Untracked) 상태 → `git add .` → commit → push.

### remote remove 후 여러 명령어를 한 번에 붙여넣었을 때

`init`(재초기화) → `add README.md`(바뀐 게 없음) → `commit`(담은 게 없어 안 됨) → `branch -M main`(이미 main) → `remote add`(끊은 연결 다시 붙임) → `push`(`Everything up-to-date`). 결과적으로 **이전과 같은 상태**, 망가진 건 없었어. 붙여넣으면 출력이 맨 아래 몰려 나와서 헷갈려.

### 이미 올라간 .DS\_Store 지우기

`.gitignore`에 넣는 것만으론 안 빠져. `git rm --cached '*.DS_Store'` → `git status`로 `deleted:` 확인 → commit → push. 이후엔 다시 안 올라가.

### GitHub 저장소를 지우고 새로 만들었을 때

Graph가 남은 건 로컬 `.git` 때문. `git remote add`는 `already exists`로 실패했고, 연결은 여전히 지운 주소였어.

- 기록 지우고 새로: `rm -rf .git` → `git init` → `git add day4/ README.md .gitignore` → commit → `remote add` → `push -u origin main`
- 기록 유지: `git remote set-url origin 새URL` → `git push -u origin main`

### 웹에서 README 수정 → 로컬 pull이 막혔을 때

1. `git pull` → 다운로드는 됐지만 로컬 README에 커밋 안 한 수정("후아")이 있어서 `Aborting`
2. `git stash` → `git pull`(Fast-forward 성공) → `git stash pop` → `CONFLICT`
3. 충돌 표시를 정리 안 하고 add → commit해서 **README에 `<<<<<<<` 표시가 그대로 커밋됨**
4. 이때 `git pull`이 `Already up to date` = 받을 게 없다는 뜻. 내 커밋은 아직 로컬에만 있어서 Graph에 **Outgoing Changes**
5. 충돌 표시 지우고 저장 → add → commit("README 충돌 정리") → push → 남은 표시 grep 확인 → `git stash drop`

**교훈:** CONFLICT가 뜨면 바로 commit하지 말고, 파일에서 표시부터 정리. 웹과 로컬을 같이 쓰면 작업 전 항상 `git pull`.

### 새 폴더(AIO\_4\_practice)에 clone이 안 될 때

폴더에 `.gitignore`가 있어 `.`으로 clone 실패 → 이후 명령은 전부 `not a git repository`. `mv .gitignore ../gitignore_backup` → clone → 백업 규칙 중 없는 것만 새 `.gitignore`에 추가 → commit → push.

### 브랜치 두 개로 PR 연습

- feature/login: 생성 → `git_practice.py` 커밋 → push → PR #1 merge → 로컬 `git switch main` → `git pull` → `git branch -d feature/login`
- feature/backend: PR #1 merge 전 main에서 갈라져 `git_practice.py`가 없음 → `git_practice2.py` 커밋 → `git push`(짝이 이미 있어서 `-u` 불필요) → PR로 main에 merge
- PR 화면: `base: main ← compare: 브랜치` 방향, `Able to merge` = 충돌 없이 합칠 수 있음. `0 additions`는 빈 파일이라서.

### 두 폴더에서 같은 저장소를 쓰다가 rejected

AIO\_4\_practice에서 PR merge → GitHub main이 앞서감 → AIO\_4\_class는 모른 채 `깃 내용 복습 업로드` 커밋 → push 시 `[rejected] (fetch first)`. `git config --global pull.rebase false` → `git pull --no-edit` → `git push`. **폴더를 바꿔 작업할 땐 항상 `git pull`부터.**

### 파일 삭제 (day4/main.py)

`git pull` → `git rm day4/main.py` → `git status` → commit → push. 이미 Finder에서 지웠으면 `git add day4/main.py`로 삭제를 담아. 로컬은 남기려면 `git rm --cached`.

## 7. README.md 검토 결과

aio4\_class\_git의 README.md(Git·GitHub·VS Code 초기 설정 및 Push 실습 가이드)는 **명령어와 절차 자체는 대부분 맞아.** 크게 틀린 건 없고, 오해할 수 있는 표현 2곳과 맥 환경·오늘 겪은 오류가 빠진 부분을 고쳤어. 수정본 README.md 파일을 따로 줬으니 덮어쓰고 commit → push 하면 돼.

### 틀리거나 오해할 수 있는 부분

| 위치 | 원래 내용 | 문제 | 수정 |
| --- | --- | --- | --- |
| 6단계 | 최초 커밋 전에는 **환경에 따라** 브랜치 목록에 표시되지 않을 수 있다 | 환경과 무관하게 커밋 전엔 항상 안 보여 | "최초 커밋 전에는 표시되지 않는다" |
| 6단계 | 대소문자를 **구분할 수 있다**. Main과 main은 동일한 이름이 아니므로 | git은 구분하지만 Windows·macOS 파일 시스템은 구분 안 해서, 둘을 섞으면 오류가 날 수 있다는 진짜 이유가 빠짐 | 이유를 명시하고 `init.defaultBranch main` 팁 추가 |
| 전체 요약 7-2 | 7번에서 add한 직후 바로 remove → 다시 add | 순서대로 따라 치면 의미 없는 반복. 주소 변경은 `set-url`이 더 간단(본문 7단계와도 불일치) | 요약에서 빼서 "필요한 경우에만" 별도 블록, `set-url` 권장으로 정리 |
| 9단계 인증 | 브라우저 로그인 또는 Credential Manager | 터미널에 Username/Password를 물을 때 비밀번호는 안 된다는 점이 없음 | 비밀번호 인증 미지원, 토큰/브라우저 로그인 안내 추가 |

### 추가한 부분

- 실습 환경에 **macOS** 추가: Homebrew로 Git 설치, VS Code를 응용 프로그램 폴더로 옮기기, `mkdir -p ~/...`, `code` 명령 설치 방법(Shell Command)
- 4단계: 잔디에 기록되려면 GitHub 등록 이메일 사용, 설정 전 커밋했을 때 `--amend --reset-author`
- 5단계: `.git`이 숨김 폴더라는 점과 Finder에서 보는 법
- 8단계: `.DS_Store` 예시, 이미 커밋된 파일은 `git rm --cached`로 빼야 한다는 점
- 2단계: `git clone 주소 .`은 빈 폴더여야 한다는 점
- 반복 작업: upstream이 있으면 `git pull`/`git push`만 써도 됨, 충돌 표시 정리 방법과 `git stash drop`
- 오류 표에 4개 추가: `CONFLICT`, `not a git repository`, `destination path ... not an empty directory`, `askpass.sh`

### 수정본 반영 방법

```bash
# 받은 README.md로 AIO_4_practice(또는 AIO_4_class)의 README.md를 덮어쓴 뒤
git pull
git add README.md
git commit -m "README 내용 보완 (macOS, 오류 사례 추가)"
git push
```
