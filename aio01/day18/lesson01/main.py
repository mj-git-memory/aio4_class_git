"""1차시: 같은 세션의 재실행 사이에 입력 메시지를 유지한다."""

# Streamlit은 화면을 만들고, 화면 조작이 일어나면 이 파일을 다시 실행한다.
import streamlit as st

print('streamlit 실행')

# 화면의 제목과 이번 실습의 범위를 안내한다.
st.title("메시지가 남는 대화 화면")
st.caption("내가 입력한 메시지만 기록합니다. AI 답변이나 로그인 기능은 없습니다.")

# messages라는 이름의 보관함이 없을 때만 빈 목록을 만든다.
# 매 실행마다 []를 대입하면 기존 메시지가 사라진다.

if "messages" not in st.session_state:
    st.session_state["messages"] = []
# messages = [] # ---> 세션을 지정하지 않고, 이렇게 메시지를 리스트로 만들어두면, 화면이 재시작 될때마다 세션이 새로 시작됨(세션 정보가 저장되지 않음)

# 버튼은 클릭으로 시작된 실행에서만 True가 된다.
# 이 버튼의 반환값은 쓰지 않는다. 재실행 후에도 기록이 남는지 확인하는 용도다.
st.button("화면 다시 실행")  # ---> 이걸 누르면 화면이 다시 시작됨

# 입력 처리와 출력보다 먼저 비워야 같은 실행에서 바로 빈 화면을 볼 수 있다.
# 현재 세션의 목록만 지우며, 다른 탭의 목록에는 영향을 주지 않는다.
if st.button("대화 비우기"):
    st.session_state["messages"] = []

# placeholder는 입력 전 안내 문구다. 제출한 실행에서는 문자열,
# 제출이 없는 실행에서는 None을 반환한다. 기본값대로 파일 첨부는 사용하지 않는다.
text = st.chat_input("메시지를 입력하고 Enter를 누르세요")
if text:
    # strip()은 앞뒤 공백을 제거한다. 공백만 있으면 빈 문자열이 된다.
    cleaned = text.strip()
    if cleaned:
        # append는 기존 목록 뒤에 메시지 한 개를 붙인다. 기존 기록은 유지된다.
        st.session_state["messages"].append({"role": "user", "content": cleaned})
        # messages.append({"role": "user", "content": cleaned})  # ---> 단순 메시지가 아닌 세션으로 만들어야, 메시지를 입력해도 이전 정보가 사라지지 않음
    else:
        st.warning("공백이 아닌 메시지를 입력하세요.")

# 추가/삭제를 끝낸 뒤 목록을 읽어 화면을 그린다. 별도 st.rerun()은 필요 없다.
st.write("저장된 메시지 수:", len(st.session_state["messages"]))
# st.write("저장된 메시지 수:", len(messages))  # ---> 세션이 아니기 때문에, 메시지를 입력할 때마다 서버 다시 시작. so 저장된 메시지 수는 항상 1개
for message in st.session_state["messages"]:
# for message in messages :
    # role은 말풍선의 발화자 표시이며, 로그인한 사용자 ID를 뜻하지 않는다.
    with st.chat_message(message["role"]):
        # 일반 텍스트로 출력해 입력한 기호를 그대로 읽을 수 있게 한다.
        st.text(message["content"])


## python -m streamlit run lesson01/main.py # 로 실행 