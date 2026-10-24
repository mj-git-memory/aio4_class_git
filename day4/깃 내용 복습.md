# Git · GitHub · VS Code 초기 설정 및 Push 실습 가이드

> **실습 목표:** 로컬 PC에 작업 폴더를 만들고, VS Code에서 프로젝트를 열어 GitHub 원격 저장소에 최초 커밋을 업로드한다.
>
> **실습 환경:** Windows 10/11 또는 macOS, Git, Visual Studio Code(VS Code), GitHub 계정
>
> 이 가이드의 경로·터미널 예시는 Windows(PowerShell) 기준이다. macOS는 각 단계의 **macOS** 참고를 따른다.

## 사전 준비

- [Git](https://git-scm.com/downloads) 설치
  - macOS: Homebrew 설치 후 `brew install git` (또는 Xcode Command Line Tools에 포함된 기본 Git 사용)
- [Visual Studio Code](https://code.visualstudio.com/) 설치
  - macOS: 다운로드한 앱을 **응용 프로그램(Applications)** 폴더로 옮긴 뒤 실행한다. 다운로드 폴더에서 바로 실행하면 업데이트 시 `read-only volume` 오류가 발생한다.
- [GitHub](https://github.com/) 계정 준비
- 터미널에서 `git --version`으로 Git 설치 확인

> **예시 정보**
> - 로컬 작업 폴더: `C:\AI4\ai4_lecture` (macOS 예: `~/AI4/ai4_lecture`)
> - GitHub 저장소: `https://github.com/skn29teacher/ai4_lecture.git`
> - 기본 브랜치: `main` (소문자)
>
> 저장소 주소와 Git 사용자 정보는 본인 환경에 맞게 변경한다. 예시 저장소로 Push하려면 해당 저장소에 쓰기 권한이 있어야 한다.

---

## 1. 로컬 PC 작업 폴더 설정

프로젝트 파일을 관리할 폴더를 만든다. VS Code의 터미널(PowerShell)에서 다음을 실행한다.

```powershell
mkdir C:\AI4\ai4_lecture
cd C:\AI4\ai4_lecture
```

macOS(zsh)에서는 다음과 같다.

```bash
mkdir -p ~/AI4/ai4_lecture
cd ~/AI4/ai4_lecture
# mkdir: 폴더를 생성합니다. make directory의 줄임말이에요.
# -p: 중간 경로의 폴더도 함께 만들고, 이미 폴더가 있어도 오류 없이 넘어갑니다.
# ~: 내 사용자 홈 폴더를 뜻해요. 현재 환경에서는 /Users/imijeong입니다.
# /AI4/ai4_lecture: AI4 폴더 안에 ai4_lecture 폴더를 만든다는 뜻이에요.
```

이미 폴더가 있다면 `mkdir`는 생략하고 `cd`만 실행한다.

**확인:** 현재 경로가 작업 폴더인지 확인한다.

```powershell
pwd
# 현재 터미널이 위치한 폴더의 전체 경로를 출력하는 명령어. Print Working Directory
```

## 2. GitHub 원격 Repository 설정

1. [GitHub](https://github.com/)에 로그인한다.
2. 오른쪽 위 **+ → New repository**를 클릭한다.
3. **Repository name**에 `ai4_lecture`를 입력한다.
4. 공개 범위를 **Public** 또는 **Private**로 선택한다.
5. **Create repository**를 클릭한다.
6. 생성된 저장소의 **HTTPS 주소**를 복사한다.

예시:

```text
https://github.com/skn29teacher/ai4_lecture.git
```

**중요:** 이 가이드는 처음부터 로컬 프로젝트를 Push하는 절차이므로, 새 원격 저장소를 생성할 때 **Add a README file**, **Add .gitignore**, **Choose a license**를 선택하지 않고 **빈 저장소**로 시작하는 것이 가장 간단하다.

원격 저장소에 이미 파일이나 커밋이 있다면, 새 폴더에서 `git clone <저장소주소>`로 시작하는 방식이 일반적으로 더 안전하다. `git clone <저장소주소> .`처럼 현재 폴더(`.`)에 받으려면 그 폴더가 **비어 있어야** 한다.
- git clone 주소	: 깃허브 저장소 이름의 폴더를 만들어 그 안에 받음
- git clone 주소 .	: 현재의 빈 폴더 안에 바로 받음


## 3. VS Code에서 작업 폴더 열기

VS Code에서 **File → Open Folder(파일 → 폴더 열기)**를 선택하고 작업 폴더를 연다.

```text
C:\AI4\ai4_lecture
```

또는 작업 폴더로 이동한 터미널에서 실행한다.

```powershell
code .
# code : VS Code를 실행하는 명령어
# . : 현재 폴더
```

`code` 명령을 사용할 수 없다면 VS Code 메뉴에서 폴더를 직접 열면 된다. macOS는 VS Code에서 `Cmd + Shift + P` → **Shell Command: Install 'code' command in PATH**를 한 번 실행해야 `code` 명령을 쓸 수 있다.

VS Code의 **Terminal → New Terminal**을 선택해 통합 터미널을 연다.

## 4. Git 사용자 이름 및 이메일 설정

Git 커밋 기록에 표시할 사용자 정보를 설정한다.

```bash
git config --global user.name "본인 Git 사용자 이름"
git config --global user.email "본인 이메일@example.com"
```

설정 결과 확인:

```bash
git config --global user.name
git config --global user.email
```

> **참고:** `--global`은 PC의 사용자 계정에 적용되는 설정이다. 특정 저장소만 다른 이름/이메일을 사용하려면 **5단계 `git init` 이후** 해당 저장소에서 `git config --local user.name "이름"` 및 `git config --local user.email "이메일"`을 실행한다.
>
> Git의 `user.name`과 `user.email`은 **커밋 작성자 정보**이며 GitHub **로그인이나 Push 권한을 부여하는 설정이 아니다**. Push할 때는 해당 저장소에 권한이 있는 GitHub 계정으로 인증해야 한다. GitHub 잔디(contribution)에 기록되려면 `user.email`이 GitHub 계정에 등록된 이메일이어야 한다.
>
> 사용자 정보를 설정하기 전에 커밋했다면, Push 전에 `git commit --amend --reset-author --no-edit`로 작성자 정보를 고칠 수 있다.
- --amend	가장 최근 커밋을 새 커밋으로 교체
- --reset-author	작성자를 현재 설정된 사용자로 바꾸고, 작성 시각도 갱신
- --no-edit	기존 커밋 메시지를 그대로 사용

## 5. Git 초기화 (`git init`)

현재 작업 폴더를 Git 저장소로 초기화한다.

```bash
git init
```

정상 실행되면 `.git` 디렉터리가 생성되고 이 폴더의 변경 이력을 Git으로 관리할 수 있다. (`.git`은 숨김 폴더라 탐색기/Finder에 기본적으로 보이지 않는다. macOS Finder는 `Cmd + Shift + .`로 숨김 파일을 볼 수 있다.)

상태 확인:

```bash
git status
```

## 6. 기본 브랜치를 `main`으로 변경

GitHub에서 일반적으로 사용하는 브랜치 이름으로 변경한다.

```bash
git branch -M main
```

> Git 브랜치 이름은 대소문자를 구분하므로 `Main`과 `main`은 서로 다른 이름이다. 다만 Windows·macOS의 기본 파일 시스템은 대소문자를 구분하지 않아 두 이름을 함께 쓰면 오류가 날 수 있으므로, 이 실습에서는 **`main`(소문자)**으로 통일한다.
>
> 매번 변경하지 않으려면 `git config --global init.defaultBranch main`을 한 번 설정해 두면 이후 `git init`부터 기본 브랜치가 `main`이 된다.

최초 커밋 전에는 브랜치 목록(`git branch`)에 아무것도 표시되지 않는다. 커밋 후 `git branch`로 확인할 수 있다.

## 7. 로컬 저장소와 원격 Repository 연결

2단계에서 복사한 GitHub HTTPS 주소를 `origin`이라는 이름으로 등록한다.

```bash
git remote add origin https://github.com/skn29teacher/ai4_lecture.git
```

연결 확인:

```bash
git remote -v
```

정상적으로 연결되면 `origin`의 `fetch` 및 `push` 주소가 표시된다.

이미 `origin`이 등록되어 있다는 오류가 나오면 중복 등록하지 않고 다음 명령으로 주소를 수정한다.

```bash
git remote set-url origin https://github.com/skn29teacher/ai4_lecture.git
```

## 8. 코드 작성 및 커밋 (`git add` / `git commit`)

VS Code에서 `README.md` 등 프로젝트 파일을 작성·저장한다.

예: `README.md`

```markdown
# ai4_lecture

Git과 GitHub를 이용한 협업 실습 저장소입니다.
```

현재 변경사항 확인:

```bash
git status
```

파일을 스테이징하고 최초 커밋을 생성한다.

```bash
git add .
git commit -m "first commit"
```

확인:

```bash
git log --oneline -1
```

> `git add .`는 현재 폴더 아래의 변경 파일을 커밋 대상으로 등록한다. 암호, API 키, 가상환경, 대용량 데이터 파일, OS가 자동 생성하는 파일(macOS `.DS_Store` 등)이 포함되지 않았는지 커밋 전에 확인하고 필요한 항목은 `.gitignore`에 추가한다.
>
> `.gitignore`는 아직 커밋되지 않은 파일에만 적용된다. 이미 커밋된 파일은 `git rm --cached <파일>`로 Git 관리에서 제외한 뒤 커밋한다.
- git rm --cached <파일> : 내 컴퓨터의 파일은 그대로 두고, Git의 관리 대상에서 제외하는 명령어
- ex) git rm --cached .env : 내 컴퓨터 - .env 파일이 그대로 남음. Git - 다음 커밋에 .env를 삭제하는 변경이 준비됨

## 9. GitHub로 Push

최초 Push에서는 원격 브랜치의 추적 관계(upstream)를 설정한다.

```bash
git push -u origin main
```

이후 같은 브랜치에서 변경사항을 업로드할 때는 간단히 실행할 수 있다.

```bash
git push
```

**최종 확인:** GitHub 저장소 페이지를 새로고침하여 `README.md` 등 프로젝트 파일과 커밋 기록이 반영되었는지 확인한다.

> **GitHub 인증:** HTTPS로 Push할 때 브라우저 로그인 또는 Git Credential Manager(macOS는 키체인/VS Code 로그인 팝업)를 통해 인증을 요청받을 수 있다. GitHub는 비밀번호 인증을 지원하지 않으므로 터미널에 `Username`/`Password`를 묻는 경우 비밀번호 대신 브라우저 로그인이나 Personal Access Token을 사용한다. 기존에 다른 계정으로 인증되어 있거나 권한이 없는 저장소로 Push하면 `403 Permission denied`가 발생할 수 있다.

---

## 전체 명령어 요약

아래 예시는 **2단계에서 원격 저장소를 빈 저장소로 생성했고, 3단계에서 VS Code 작업 폴더를 열었으며, `README.md` 파일을 작성한 상태**를 전제로 한다.

```bash
# 4. Git 작성자 정보 설정
git config --global user.name "본인 Git 사용자 이름"
git config --global user.email "본인 이메일@example.com"

# 5. Git 초기화
git init

# 6. 기본 브랜치 이름 설정
git branch -M main

# 7. 원격 저장소 연결
git remote add origin https://github.com/skn29teacher/ai4_lecture.git

# 8. 변경사항 커밋
git add .
git commit -m "first commit"

# 9. 최초 Push
git push -u origin main
```

원격 저장소 주소를 바꿔야 할 때(필요한 경우에만):

```bash
# 주소만 변경 (권장)
git remote set-url origin https://github.com/skn29teacher/ai4_lecture.git

# 또는 기존 연결을 삭제하고 다시 연결
git remote remove origin
git remote add origin https://github.com/skn29teacher/ai4_lecture.git
```

## 이후 반복 작업: Pull → 수정 → Commit → Push

최초 연결 이후에는 원격 저장소의 변경사항을 확인하고 가져온 다음 작업하는 습관을 권장한다.

```bash
# 원격 최신 코드 반영 (커밋하지 않은 로컬 변경사항이 없는 상태에서)
git pull --rebase origin main

# VS Code에서 파일 수정 및 저장

# 변경사항 확인
git status

# 수정 내용 커밋
git add .
git commit -m "Update project files"

# 원격 저장소에 업로드
git push origin main
```

upstream이 설정된 브랜치에서는 `git pull`, `git push`만 실행해도 된다.

로컬 변경사항이 있어 `git pull`이 중단된 경우에는 먼저 커밋하거나, 아래처럼 임시 보관 후 다시 적용할 수 있다.

```bash
git stash push -u -m "backup before pull" # 작업을 잠시 보관
git pull --rebase origin main 
# GitHub의 main 내용을 가져오고, 아직 push하지 않은 로컬 커밋이 있다면 그 뒤에 다시 적용
git stash pop 
# 보관한 작업을 다시 꺼내기. 임시 보관한 변경을 현재 파일에 다시 적용

# **“아직 커밋하지 않은 작업을 잠시 보관 → GitHub의 최신 내용 반영 → 보관한 작업 다시 꺼내기”**
# stash : 작업 중인 변경을 임시로 넣어 두는 보관함
# stash push : 커밋하지 않은 변경을 임시 보관하고 작업 폴더에서 치움
# -u : 새로 만든 파일처럼 Git이 아직 관리하지 않는 파일도 포함
# -m : "backup before pull"	보관한 작업에 설명을 붙임
```

`git stash pop`에서 파일 충돌이 발생하면 파일에 남은 `<<<<<<<`, `=======`, `>>>>>>>` 표시를 정리해 **충돌을 해결한 뒤** `git add` → `git commit` → `git push` 순서로 진행한다. 충돌 표시가 남은 상태로 커밋·Push하지 않는다. 충돌로 인해 stash가 자동 삭제되지 않았다면 해결 후 `git stash drop`으로 정리한다.
```python 
<<<<<<< Updated upstream
message = "반가워"
=======
message = "안녕하세요"
>>>>>>> Stashed changes

- <<<<<<< Updated upstream 아래: 현재 파일에 있는 내용
- ======= 아래: stash에서 꺼낸 내 변경
- >>>>>>> Stashed changes: 충돌 구간의 끝
```

## 자주 발생하는 오류

| 오류 메시지/상황 | 원인 | 해결 방법 |
|---|---|---|
| `remote origin already exists` | 이미 `origin`이 등록됨 | `git remote -v` 확인 후 `git remote set-url origin <주소>` |
| `403 Permission denied` | GitHub 로그인 계정에 Push 권한이 없음 | 사용 중인 GitHub 인증 계정 및 저장소 쓰기 권한 확인 |
| `Please tell me who you are` | Git 작성자 이름·이메일 미설정 | `git config --global user.name` 및 `user.email` 설정 |
| `nothing to commit, working tree clean` | 커밋할 새 변경사항이 없음 | 변경한 파일이 실제 저장되었는지 `git status` 확인 |
| `failed to push some refs` / `non-fast-forward` | 원격 브랜치에 로컬에 없는 커밋 존재 | 로컬 변경사항을 먼저 정리한 뒤 `git pull --rebase origin main` 후 Push |
| `Your local changes ... would be overwritten by merge` | Pull 시 로컬 수정사항이 덮어써질 위험 | 변경사항을 커밋하거나 `git stash`로 보관한 뒤 Pull (필요 없는 수정은 `git restore <파일>`) |
| `CONFLICT (content): Merge conflict in <파일>` | 같은 부분을 로컬과 원격에서 모두 수정 | 파일의 충돌 표시 정리 → 저장 → `git add` → `git commit` |
| `fatal: not a git repository` | Git 저장소가 아닌 폴더에서 명령 실행 | 작업 폴더 경로 확인 후 `git init` 또는 `git clone` |
| `destination path '.' already exists and is not an empty directory` | 비어 있지 않은 폴더에 clone | 빈 폴더에서 clone하거나 `.` 없이 clone해 하위 폴더 생성 |
| `cannot exec '.../askpass.sh': No such file or directory` | VS Code 터미널이 삭제·이동된 VS Code 앱 경로를 참조 | VS Code를 완전히 종료 후 다시 실행하고 새 터미널에서 Push |

---

**실습 완료 기준:** 로컬 작업 폴더에서 `git status`를 실행해 상태를 확인할 수 있고, GitHub 원격 저장소의 `main` 브랜치에 작성한 코드와 커밋이 정상적으로 나타난다.
