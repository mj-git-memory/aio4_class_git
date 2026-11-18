'''
main1.py main2.py를 다음 조건으로 확장 또는 수정
주제 : 요청 / 수신 / 완료 상태를 구분해 안내하기
    import as streamlit as st
    st.status()로 현재 진행 상태를 안내하는 화면을 추가 (더한다)
    첫 글자가 오기 전과 수신 중의 안내 문구를 구분
    완료 상태를 접거나 펼치는 기준을 바꿔 보기

    문제 : 첫 글자가 오기 전에 빈 화면은 앱이 멈춘 것처럼 보임. 글자가 나오기 시작한 뒤에도 완료인지 알 수 없음
    개선 : 요청 전에는 '요청 중', 첫번째 텍스트 수신 후에는 '수신 중', 완료를 확인 후에는 '완료'로 변경
    새로 작성된 코드에는 main1.py와 mian2.py에서 어느 부분이 수정되었는지, 간략하게 표시
'''

import os
import time
# [main2 대비 수정] 별도 스레드 없이 스트림 이벤트를 읽으며 진행 상태를 갱신합니다.
import streamlit as st
from dotenv import load_dotenv
from openai import APIError, OpenAI

load_dotenv()

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

# [main2 대비 수정] 여행 프롬프트를 main1.py의 요리 프롬프트로 교체했습니다.
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


# [main1 대비 수정] 일괄 수신 대신 스트리밍으로 첫 텍스트와 완료 시점을 구분합니다.
# [main2 대비 수정] status 파라미터를 추가해 첫 텍스트 수신 시 안내를 갱신합니다.
def render_answer(client, inputs, stats, status):
    """스트림을 수신하며 상태를 바꾸고, 완성된 답변을 반환합니다.

    client: Groq API 클라이언트, inputs: 시스템 지침과 대화 메시지 목록
    stats: 첫 텍스트/완료 시간과 부분 답변을 저장할 사전
    status: main에서 만든 st.status 컨테이너
    """
    started = time.perf_counter()
    stats.update(first=None, total=None, partial='', updates=0, completed=False)
    try:
        with client.responses.create(
            model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b').strip(),
            input=inputs,
            stream=True,  # 텍스트가 처음 도착하는 시점과 완료 이벤트를 구분합니다.
            store=False,  # 대화는 Streamlit 세션에서 관리합니다.
        ) as stream:
            for event in stream:
                if event.type == 'response.output_text.delta' and event.delta:
                    if stats['first'] is None:
                        stats['first'] = time.perf_counter() - started
                        # 연결/상태 이벤트가 아닌 첫 번째 실제 텍스트 수신 시 전환합니다.
                        status.update(label='수신 중', state='running', expanded=True)
                        status.write('답변 텍스트를 받고 있습니다. 완료 후 답변을 표시합니다.')
                    stats['partial'] += event.delta
                    stats['updates'] += 1
                elif event.type == 'response.completed':
                    stats['total'] = time.perf_counter() - started
                    stats['completed'] = True
                    break
                elif event.type in ('response.failed', 'response.incomplete', 'error'):
                    raise ValueError('서버가 답변 생성을 완료하지 못했습니다. 다시 시도해주세요.')

        # 스트림 종료만으로 성공을 판단하지 않고 완료 이벤트와 답변을 확인합니다.
        if not stats['completed']:
            raise ValueError('완료 확인 전에 연결이 종료되었습니다. 다시 시도해주세요.')
        if not stats['partial'].strip():
            raise ValueError('답변 텍스트가 비어 있습니다. 다시 질문해주세요.')
        return stats['partial']
    finally:
        if stats['total'] is None:
            stats['total'] = time.perf_counter() - started


# [추가] 완료 상태를 접거나 펼칠 조건을 별도 함수로 분리했습니다.
def should_expand(policy, total, threshold):
    """policy: 완료 표시 방식, total: 전체 응답 시간, threshold: 긴 응답 기준(초)."""
    if policy == '항상 펼치기':
        return True
    if policy == '긴 응답만 펼치기':
        return total >= threshold
    return False


# [main2 대비 수정] 시간 표시를 함수로 분리해 이전 대화와 현재 답변에 재사용합니다.
def timing_text(stats):
    """같은 요청 시작 시점을 기준으로 측정한 두 시간을 표시합니다."""
    first = stats.get('first')
    first_text = f'{first:.2f}초' if first is not None else '수신하지 못함'
    return f"첫 텍스트 수신: {first_text} · 전체 응답: {stats['total']:.2f}초"


def main():
    st.set_page_config(page_title='요리 AI · 진행 상태', page_icon='🍳')
    st.title('🍳 요리 AI 어시스턴트')
    st.caption('요청 중 → 수신 중 → 완료 상태를 확인하며 요리를 질문해보세요.')

    # [main2 대비 수정] 대기 안내 기준 대신 완료 상태의 접기/펼치기 정책을 선택합니다.
    # 완료 상태의 접기/펼치기 정책을 바꿔 결과를 비교할 수 있습니다.
    policy = st.sidebar.selectbox(
        '완료 상태 표시',
        ['항상 접기', '항상 펼치기', '긴 응답만 펼치기'],
    )
    threshold = st.sidebar.number_input(
        '긴 응답 기준(초)', min_value=1.0, max_value=60.0, value=5.0, step=1.0,
        help='전체 응답 시간이 이 값 이상이면 긴 응답으로 분류합니다.',
    )

    # main1/main2와 다른 키를 사용해 이 실습의 요리 대화만 저장합니다.
    if 'cooking_status_messages' not in st.session_state:
        st.session_state.cooking_status_messages = []
    messages = st.session_state.cooking_status_messages

    # [추가] 저장된 답변에도 완료 상태와 응답 시간을 다시 표시합니다.
    for message in messages:
        with st.chat_message(message['role']):
            if message['role'] == 'assistant':
                stats = message['stats']
                # 이전 답변도 현재 선택한 완료 표시 정책에 맞춰 다시 그립니다.
                finished = st.status(
                    '완료', state='complete',
                    expanded=should_expand(policy, stats['total'], threshold),
                )
                finished.write('요리 답변을 모두 받았습니다.')
                finished.caption(timing_text(stats))
            st.markdown(message['content'])

    question = st.chat_input(placeholder='예: 달걀과 두부로 2인분 요리 추천해줘')
    if not question or not question.strip():
        return
    question = question.strip()

    with st.chat_message('user'):
        st.markdown(question)

    # stats는 화면용 정보이므로 API에는 role과 content만 전달합니다.
    history = [{'role': item['role'], 'content': item['content']} for item in messages]
    inputs = build_input(history, question)
    stats = {}

    with st.chat_message('assistant'):
        # [main1/main2 대비 수정] spinner/안내 문구를 st.status의 단계별 상태로 변경했습니다.
        # API 호출 전에 표시합니다. label: 안내 문구, state: 아이콘, expanded: 펼침 여부
        status = st.status('요청 중', state='running', expanded=True)
        status.write('요리 답변을 요청합니다. 첫 텍스트를 기다리고 있어요.')
        try:
            with create_client() as client:
                answer = render_answer(client, inputs, stats, status)
        except (APIError, ValueError) as error:
            # [추가] 오류 상태를 표시하고, 미완성 답변은 별도 expander에서 확인합니다.
            # 오류가 발생하면 완료로 바꾸지 않고 상세 내용을 펼쳐 둡니다.
            status.update(label='오류', state='error', expanded=True)
            if isinstance(error, APIError):
                status.error('요청에 실패했습니다. API 키, 모델명, 사용 한도와 네트워크를 확인해주세요.')
            else:
                status.error(str(error))
            if stats.get('total') is not None:
                status.caption(timing_text(stats))
            if stats.get('partial'):
                with st.expander('중단 전 수신한 내용 (미완성)'):
                    st.markdown(stats['partial'])
            return

        status.write('요리 답변을 모두 받았습니다.')
        status.caption(timing_text(stats))
        # [추가] 완료 확인 후 선택한 정책에 따라 상태 상자를 접거나 펼칩니다.
        # 완료 이벤트 확인과 답변 검증을 마친 뒤에만 완료 아이콘으로 전환합니다.
        status.update(
            label='완료', state='complete',
            expanded=should_expand(policy, stats['total'], threshold),
        )
        # 답변은 상태 컨테이너 밖에 표시해 상태를 접어도 계속 볼 수 있습니다.
        st.markdown(answer)

    # [main1/main2 대비 수정] 경과 시간/표시 문구 대신 stats 사전을 저장해 다시 활용합니다.
    # 성공한 대화만 저장합니다. 부분 답변 문자열은 content와 중복되므로 제외합니다.
    saved_stats = {key: value for key, value in stats.items() if key != 'partial'}
    messages.extend([
        {'role': 'user', 'content': question},
        {'role': 'assistant', 'content': answer, 'stats': saved_stats},
    ])


if __name__ == '__main__':
    main()

# 실행: streamlit run day20/main3.py
