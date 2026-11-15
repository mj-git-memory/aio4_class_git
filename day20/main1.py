import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import APIError, OpenAI
load_dotenv()

# Groq 모델 생성 함수
def create_client() :
    key = os.getenv('GROQ_API_KEY', '').strip()
    if not key:
        raise ValueError('.env 파일에 GROQ_API_KEY를 설정해주세요.')
    args = {
        'api_key':key, 'base_url':'https://api.groq.com/openai/v1',
        # timeout: 요청 대기 시간(초), max_retries: 실패 시 자동 재시도 횟수
        'timeout':60.0, 'max_retries':0
    }
    return OpenAI(**args)

def build_input(history, question) : 
    system_messages = {
        'role': 'system',
        'content': (
            "당신은 전문 셰프이자 친절한 요리 AI 어시스턴트입니다.\n"
            "사용자의 질문과 대화 기록을 바탕으로 정확하고 실용적인 요리 정보를 제공합니다.\n\n"

            "## 역할\n"
            "1. 한식, 양식, 중식, 일식 등 다양한 요리의 레시피를 안내합니다.\n"
            "2. 사용자가 보유한 재료를 활용해 만들 수 있는 요리를 추천합니다.\n"
            "3. 요리 초보자도 이해할 수 있도록 쉽고 구체적으로 설명합니다.\n"
            "4. 재료 대체, 조리법 변경, 음식 보관 및 식재료 관리 방법을 안내합니다.\n"
            "5. 사용자의 취향, 알레르기, 식단 제한, 조리 환경을 고려합니다.\n\n"

            "## 응답 원칙\n"
            "1. 사용자의 질문에 직접적으로 답하고 불필요한 설명은 최소화합니다.\n"
            "2. 레시피 요청 시 재료, 분량, 조리 시간, 조리 순서를 명확히 안내합니다.\n"
            "3. 재료의 분량은 g, ml, 큰술, 작은술 등 구체적인 단위로 표시합니다.\n"
            "4. 조리 과정은 번호를 붙여 단계별로 설명합니다.\n"
            "5. 조리 온도와 시간은 가능한 한 구체적으로 안내하되, "
            "재료와 조리 환경에 따라 달라질 수 있음을 고려합니다.\n"
            "6. 사용자가 가진 재료가 부족하다면 가능한 대체 재료를 제안합니다.\n"
            "7. 사용자가 조리 인원이나 식단 조건을 지정하면 이를 우선 반영합니다.\n"
            "8. 필수 정보가 부족하면 필요한 질문을 간결하게 하되, "
            "합리적인 기본값으로 답변할 수 있다면 먼저 안내합니다.\n"
            "9. 앞선 대화에서 확인된 취향이나 조건을 일관되게 반영합니다.\n"
            "10. 확인되지 않은 사실을 단정하거나 존재하지 않는 조리법을 지어내지 않습니다.\n\n"

            "## 식품 안전\n"
            "1. 식중독 예방을 위해 위생적인 재료 손질과 조리 방법을 안내합니다.\n"
            "2. 육류, 생선, 달걀 등은 안전한 조리 상태와 보관 방법을 고려합니다.\n"
            "3. 알레르기 유발 식품이 포함된 경우 사용자가 알려준 알레르기 정보를 우선 적용합니다.\n"
            "4. 상했을 가능성이 있는 식재료는 섭취를 권장하지 않습니다.\n"
            "5. 음식의 안전성이 불확실한 경우 임의로 안전하다고 판단하지 않습니다.\n\n"

            "## 응답 형식\n"
            "레시피를 요청한 경우 다음 형식을 기본으로 사용합니다.\n"
            "🍳 요리 이름\n"
            "⏱ 예상 조리 시간 및 인분\n"
            "🥕 필요한 재료와 분량\n"
            "👨‍🍳 단계별 조리 방법\n"
            "💡 요리 팁 및 대체 재료 (필요한 경우)\n\n"

            "단순한 요리 관련 질문에는 위 형식을 강제하지 않고 "
            "질문의 목적에 맞춰 간결하게 답변합니다.\n\n"

            "## 언어 및 대화 스타일\n"
            "1. 모든 답변은 기본적으로 한국어로 작성합니다.\n"
            "2. 친절하고 자연스러운 말투를 사용합니다.\n"
            "3. 전문 요리 용어는 필요한 경우 쉬운 설명을 함께 제공합니다.\n"
            "4. 사용자의 요리 경험 수준에 맞춰 설명의 난이도를 조절합니다.\n\n"

            "## 대화 범위\n"
            "요리, 식재료, 조리 도구, 식단 구성, 식품 보관 등 "
            "음식과 관련된 질문을 전문적으로 다룹니다.\n"
            "요리와 무관한 질문에는 요리 전문 어시스턴트임을 간단히 안내하고 "
            "관련 질문을 유도합니다."
        )
    }
    return [system_messages] + history + [{'role': 'user', 'content': question}]


# 서버의 응답 함수 -> 답변을 한번에 생성하기 
def render_answer(client, input_items) :
    # client: Groq 서버에 연결한 OpenAI 클라이언트
    # input_items: 시스템 지침 + 이전 대화 + 현재 질문이 담긴 메시지 목록
    response = client.chat.completions.create(
        model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b').strip(),
        messages=input_items,
        stream=False,  # 답변을 조각으로 받지 않고 완성된 상태로 한 번에 받습니다.
    )
    answer = response.choices[0].message.content
    if not answer or not answer.strip():
        raise ValueError('답변이 비어 있습니다. 질문을 다시 입력해주세요.')
    return answer

# 메인 함수 UX (streamlit)
def main():
    st.set_page_config(page_title='요리 AI 어시스턴트', page_icon='🍳')
    st.title('🍳 요리 AI 어시스턴트')
    st.caption('가지고 있는 재료나 궁금한 요리를 알려주세요.')

    # session_state는 입력할 때마다 스크립트가 재실행되어도 대화 기록을 유지합니다.
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        # name에 해당하는 role(user/assistant)에 따라 대화 말풍선을 표시합니다.
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            if 'elapsed' in message:
                st.caption(f"⏱ 응답 시간: {message['elapsed']:.2f}초")

    # placeholder: 질문 입력창에 표시할 안내 문구
    question = st.chat_input(placeholder='예: 달걀과 두부로 만들 수 있는 요리 알려줘')
    if not question or not question.strip():
        return
    question = question.strip()
    started_at = time.perf_counter()

    with st.chat_message('user'):
        st.markdown(question)

    # API에는 role과 content만 전달하고, 화면 표시용 응답 시간은 제외합니다.
    history = [
        {'role': message['role'], 'content': message['content']}
        for message in st.session_state.messages
    ]
    # history: 이전 대화 목록, question: 이번 질문 (중복되지 않도록 별도로 전달)
    input_items = build_input(history, question)

    with st.chat_message('assistant'):
        try:
            with st.spinner('요리 답변을 준비하고 있어요...'):
                # 요청이 끝나면 연결을 닫아 클라이언트 자원을 정리합니다.
                with create_client() as client:
                    answer = render_answer(client, input_items)
            elapsed = time.perf_counter() - started_at
        except APIError:
            st.error('답변 요청에 실패했습니다. API 키, 모델명, 사용 한도와 네트워크를 확인해주세요.')
            return
        except ValueError as error:
            st.error(str(error))
            return

        st.markdown(answer)
        st.caption(f'⏱ 응답 시간: {elapsed:.2f}초')

    # 성공한 질문과 답변을 함께 저장합니다. 응답 시간도 저장해 재실행 후 표시합니다.
    st.session_state.messages.extend([
        {'role': 'user', 'content': question},
        {'role': 'assistant', 'content': answer, 'elapsed': elapsed},
    ])


if __name__ == '__main__':
    main()


# streamlit run day20/main1.py # 로 실행