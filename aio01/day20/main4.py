"""
main3.py를 다음과 같이 확장
확장의 개념은 점진적인 개선임

[개선안]
미완성 질문 보관, 한번 실패 시키기, 재시도 또는 취소의 기능을 더함
첫 조각 이후 수신이 끊기는 상황을 버튼으로 재현
미완성 질문을 재시도하거나 취소하고, 성공 기록의 변화를 확인 
글자가 화면에 나왔다고 해서 완성된 답변이 아니고, 
중간에 끊긴 답변을 정상 대화에 넣으면, 이후 질문이 불완전한 내용을 참조하게 되는 잘못된 현상 발생
제출한 질문은 pending에 넣고 잠시 보관하다가, 정상 완료 후에만 질문 답변을 성공 목록에 넣음 
"""

import os
import time
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

def should_expand(policy, total, threshold):
    """policy: 완료 표시 방식, total: 전체 응답 시간, threshold: 긴 응답 기준(초)."""
    if policy == '항상 펼치기':
        return True
    if policy == '긴 응답만 펼치기':
        return total >= threshold
    return False

def timing_text(stats):
    """같은 요청 시작 시점을 기준으로 측정한 두 시간을 표시합니다."""
    first = stats.get('first')
    first_text = f'{first:.2f}초' if first is not None else '수신하지 못함'
    return f"첫 텍스트 수신: {first_text} · 전체 응답: {stats['total']:.2f}초"


# [main3 대비 추가] 실제 API 오류와 실습용 강제 중단을 구분합니다.
class SimulatedDisconnect(RuntimeError):
    pass


def render_answer(client, inputs, stats, status, answer_box, fail_after_first=False):
    """client: API 연결, inputs: 성공 기록 + 현재 질문, stats: 이번 시도의 수신 결과.

    status: 진행 상태, answer_box: 미완성 텍스트 표시 영역
    fail_after_first: True이면 첫 텍스트 조각을 표시한 직후 예외 발생
    """
    started = time.perf_counter()
    stats.update(first=None, total=None, partial='', updates=0, completed=False)
    completed = False
    try:
        with client.responses.create(
            model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b').strip(),
            input=inputs, stream=True, store=False,
        ) as stream:
            for event in stream:
                if event.type == 'response.output_text.delta' and event.delta:
                    if stats['first'] is None:
                        stats['first'] = time.perf_counter() - started
                        status.update(label='수신 중', state='running', expanded=True)
                        status.write('텍스트를 받고 있습니다. 아직 완성된 답변이 아닙니다.')
                    stats['partial'] += event.delta
                    stats['updates'] += 1
                    # [main3 대비 수정] 미완성 답변도 표시하되 성공 기록에는 넣지 않습니다.
                    answer_box.markdown(stats['partial'] + ' ▌')
                    if fail_after_first:
                        raise SimulatedDisconnect('실습: 첫 텍스트 조각 수신 후 연결을 한 번 중단했습니다.')
                elif event.type == 'response.completed':
                    stats['total'] = time.perf_counter() - started
                    completed = True
                    break
                elif event.type in ('response.failed', 'response.incomplete', 'error'):
                    raise ValueError('서버가 답변 생성을 완료하지 못했습니다.')
        if not completed:
            raise ValueError('완료 이벤트를 받기 전에 연결이 끊겼습니다.')
        if not stats['partial'].strip():
            raise ValueError('답변 텍스트가 비어 있습니다.')
        stats['completed'] = True
        return stats['partial']
    finally:
        if stats['total'] is None:
            stats['total'] = time.perf_counter() - started


# [main3 대비 추가] 성공한 질문/답변 한 쌍을 함께 반영하고 pending을 비웁니다.
def commit_success(state, answer, stats):
    """state: 세션의 대화 상태, answer/stats: 완료 검증을 마친 답변과 측정 결과."""
    pending = state['pending']
    if pending is None or not stats.get('completed') or not answer.strip():
        raise ValueError('완료된 질문과 답변만 성공 기록에 저장할 수 있습니다.')
    saved_stats = {key: value for key, value in stats.items() if key != 'partial'}
    state.update(
        messages=state['messages'] + [
            {'role': 'user', 'content': pending['question']},
            {'role': 'assistant', 'content': answer, 'stats': saved_stats},
        ],
        pending=None,
    )


def cancel_pending(state):
    """성공 기록은 유지하고 미완성 질문/답변과 실패 예약을 취소합니다."""
    state.update(pending=None, fail_next=False, notice='미완성 질문을 취소했습니다. 성공 기록은 유지됩니다.')


def run_pending(state):
    """ready 상태의 질문만 실행합니다. 실패 시 질문과 부분 답변을 pending에 보관합니다."""
    pending = state['pending']
    pending['state'] = 'running'
    pending['attempts'] += 1
    pending['stats'] = {}  # 재시도는 이전 부분 답변에 이어 붙이지 않고 새로 생성합니다.
    pending['error'] = ''
    # [main3 대비 수정] 미완성 답변을 제외한 성공 기록만 API의 이전 대화로 사용합니다.
    history = [{'role': m['role'], 'content': m['content']} for m in state['messages']]
    inputs = build_input(history, pending['question'])

    with st.chat_message('assistant'):
        status = st.status('요청 중', state='running', expanded=True)
        status.write('첫 텍스트를 기다립니다. 질문은 아직 pending에 보관 중입니다.')
        answer_box = st.empty()
        try:
            with create_client() as client:
                answer = render_answer(
                    client, inputs, pending['stats'], status, answer_box,
                    fail_after_first=state['fail_next'],
                )
        except (APIError, ValueError, SimulatedDisconnect) as error:
            if isinstance(error, SimulatedDisconnect):
                # [추가] 실제 첫 조각에서 중단한 경우에만 예약을 소진하여 재시도는 정상 진행합니다.
                state['fail_next'] = False
            pending['state'] = 'failed'
            pending['error'] = (
                'API 요청에 실패했습니다. 키, 모델명, 사용 한도와 네트워크를 확인해주세요.'
                if isinstance(error, APIError) else str(error)
            )
            status.update(label='중단 · 재시도 또는 취소 필요', state='error', expanded=True)
        else:
            commit_success(state, answer, pending['stats'])
            status.update(label='완료', state='complete', expanded=False)
            state['notice'] = '완료된 질문과 답변 한 쌍을 성공 기록에 저장했습니다.'
    # 실패 화면의 재시도/취소 버튼 또는 완료된 성공 기록을 즉시 다시 그립니다.
    st.rerun()


def main():
    st.set_page_config(page_title='요리 AI · 재시도와 취소', page_icon='🍳')
    st.title('🍳 요리 AI 어시스턴트')
    st.caption('요청 중 → 수신 중 → 완료 · 중단된 질문은 재시도하거나 취소할 수 있습니다.')

    # [main3 대비 추가] 성공 기록과 미완성 질문을 명확히 분리하여 세션에 보관합니다.
    if 'cooking_retry' not in st.session_state:
        st.session_state.cooking_retry = {
            'messages': [], 'pending': None, 'fail_next': False, 'notice': '',
        }
    state = st.session_state.cooking_retry
    pending = state['pending']
    # 설정 변경 등으로 실행이 중단되면 자동 재요청하지 않고 사용자가 재시도를 선택합니다.
    if pending is not None and pending['state'] == 'running':
        pending['state'] = 'failed'
        pending['error'] = '이전 실행이 중단되었습니다. 재시도하거나 취소해주세요.'

    policy = st.sidebar.selectbox('완료 상태 표시', ['항상 접기', '항상 펼치기', '긴 응답만 펼치기'])
    threshold = st.sidebar.number_input('긴 응답 기준(초)', min_value=1.0, max_value=60.0, value=5.0, step=1.0)
    # [추가] 버튼으로 다음 질문의 첫 텍스트 조각 이후 중단을 예약합니다.
    if st.sidebar.button('다음 요청 한 번 실패시키기', disabled=pending is not None or state['fail_next']):
        state['fail_next'] = True
    if state['fail_next']:
        st.sidebar.warning('실패 실습 예약 중: 첫 텍스트 조각을 받은 직후 한 번 중단합니다.')
    st.sidebar.caption('실패 예약 버튼을 누른 뒤 질문을 제출해보세요. 실제 API를 호출합니다.')
    st.sidebar.metric('성공한 대화 수', len(state['messages']) // 2)
    st.sidebar.caption(f"미완성 질문: {'있음' if pending is not None else '없음'}")

    if state['notice']:
        st.info(state['notice'])
        state['notice'] = ''

    for message in state['messages']:
        with st.chat_message(message['role']):
            if message['role'] == 'assistant':
                stats = message['stats']
                finished = st.status('완료', state='complete', expanded=should_expand(policy, stats['total'], threshold))
                finished.write('정상 완료되어 성공 기록에 저장된 답변입니다.')
                finished.caption(timing_text(stats))
            st.markdown(message['content'])

    # [추가] 실습에서 실패/취소/성공 전후의 기록 변화를 확인합니다.
    with st.expander('성공 기록 확인'):
        st.json([{'role': m['role'], 'content': m['content']} for m in state['messages']])

    if pending is not None:
        with st.chat_message('user'):
            st.markdown(pending['question'])
            st.caption(f"미완성 질문 · 시도 횟수: {pending['attempts']}")
        if pending['state'] == 'failed':
            with st.chat_message('assistant'):
                failed = st.status('중단 · 재시도 또는 취소 필요', state='error', expanded=True)
                failed.error(pending['error'])
                failed.write('이 질문과 미완성 답변은 성공 기록에 포함되지 않았습니다.')
                if pending['stats'].get('total') is not None:
                    failed.caption(timing_text(pending['stats']))
                if pending['stats'].get('partial'):
                    st.warning('미완성 답변입니다.')
                    st.markdown(pending['stats']['partial'])
            retry_col, cancel_col = st.columns(2)
            # 재시도 버튼을 눌러야만 ready로 전환하여 같은 질문을 다시 실행합니다.
            if retry_col.button('재시도', type='primary'):
                pending['state'] = 'ready'
                st.rerun()
            if cancel_col.button('취소'):
                cancel_pending(state)
                st.rerun()
        elif pending['state'] == 'ready':
            run_pending(state)

    # pending이 남아 있는 동안 새 질문 제출을 막아 처리할 질문을 하나로 유지합니다.
    question = st.chat_input('예: 달걀과 두부로 만들 수 있는 요리 알려줘', disabled=state['pending'] is not None)
    if question and question.strip():
        # [핵심 변경] 제출 시에는 성공 기록을 건드리지 않고 pending에만 저장합니다.
        state['pending'] = {
            'question': question.strip(), 'state': 'ready',
            'attempts': 0, 'stats': {}, 'error': '',
        }
        st.rerun()


if __name__ == '__main__':
    main()

# 실행: streamlit run day20/main4.py
