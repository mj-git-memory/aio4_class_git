"""
주제 : 긴 답변의 화면 갱신 단위와 읽기 영역 개선
텍스트를 묶어 보내는 생성기와 높이가 정해진 읽기 영역 구현 

모델 텍스트를 모아서 화면에 보내는 갱신 단위를 변경
줄바꿈과 마지막 남은 조각이 사라지지 않는지 확인

조각마다 바로 갱신하면 긴 markdown 답변의 줄과 목록이 자주 변경되는 문제를 개선
너무 오래 모으면 첫 응답이 늦게 보임 -> 기준을 정하라 필요 있음
인위적으로 늦추는 sleep은 사용 안함 
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
    """수신/표시 시간과 API 조각 수/화면 갱신 수를 나누어 보여줍니다."""
    first = stats.get('first')
    shown = stats.get('first_display')
    first_text = f'{first:.2f}초' if first is not None else '수신하지 못함'
    shown_text = f'{shown:.2f}초' if shown is not None else '표시하지 못함'
    return (
        f"첫 텍스트 수신: {first_text} · 첫 화면 표시: {shown_text} · "
        f"전체 응답: {stats['total']:.2f}초 · "
        f"수신 조각: {stats['updates']}개 · 화면 갱신: {stats['screen_updates']}회"
    )


# [main3 대비 추가] 실제 API 오류와 실습용 강제 중단을 구분합니다.
class SimulatedDisconnect(RuntimeError):
    pass


# [main4 대비 추가] 원본 텍스트를 훼손하지 않고 묶어서 내보내는 생성기입니다.
def batch_text(chunks, min_chars=80, max_wait=0.15, clock=None):
    """chunks: 텍스트 생성기, min_chars: 갱신 글자 수, max_wait: 갱신 간격(초).

    첫 조각은 바로 전달합니다. 이후 글자 수 또는 시간 기준을 충족하면 전달합니다.
    시간 기준은 조각이 도착할 때 확인하므로, 서버 수신이 막힌 동안의 타이머는 아닙니다.
    clock: 테스트용 시계 주입. 실행 중에는 perf_counter를 사용합니다.
    """
    if min_chars < 1 or max_wait <= 0:
        raise ValueError('갱신 글자 수와 갱신 간격은 양수여야 합니다.')
    clock = clock or time.perf_counter
    buffer = []
    size = 0
    first = True
    last_flush = clock()
    try:
        for chunk in chunks:
            if not chunk:
                continue
            buffer.append(chunk)  # strip/split을 사용하지 않아 줄바꿈과 공백이 보존됩니다.
            size += len(chunk)
            now = clock()
            if first or size >= min_chars or now - last_flush >= max_wait:
                text = ''.join(buffer)
                buffer = []
                size = 0
                first = False
                last_flush = now
                yield text
    except Exception:
        # 수신 오류 직전 버퍼도 화면에 전달하되, 예외를 다시 발생시켜 성공을 막습니다.
        if buffer:
            yield ''.join(buffer)
        raise
    else:
        # 완료 시 기준보다 짧은 마지막 조각도 반드시 전달합니다.
        if buffer:
            yield ''.join(buffer)


# [main4 대비 수정] API 수신과 화면 갱신을 분리하여 텍스트 조각만 yield합니다.
def stream_text(client, inputs, stats, status, fail_after_first=False):
    started = time.perf_counter()
    stats.update(first=None, first_display=None, total=None, partial='', updates=0,
                 screen_updates=0, completed=False, started=started)
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
                        status.write('텍스트를 묶어 표시하고 있습니다. 아직 미완성 답변입니다.')
                    stats['partial'] += event.delta
                    stats['updates'] += 1
                    yield event.delta
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
    finally:
        if stats['total'] is None:
            stats['total'] = time.perf_counter() - started


def render_answer(client, inputs, stats, status, answer_box, fail_after_first=False,
                  min_chars=80, max_wait=0.15):
    """answer_box: 고정 높이 영역 안의 출력 위치, min_chars/max_wait: 묶음 갱신 기준."""
    chunks = stream_text(client, inputs, stats, status, fail_after_first)
    displayed = ''
    try:
        for batch in batch_text(chunks, min_chars=min_chars, max_wait=max_wait):
            displayed += batch
            # write_stream의 타자 효과 없이, 묶음당 한 번만 전체 Markdown을 갱신합니다.
            answer_box.markdown(displayed)
            stats['screen_updates'] += 1
            if stats['first_display'] is None:
                stats['first_display'] = time.perf_counter() - stats['started']
    finally:
        chunks.close()  # 화면 갱신 중 예외가 발생해도 API 스트림을 정리합니다.
    if displayed != stats['partial']:
        raise ValueError('수신 텍스트와 화면 텍스트가 일치하지 않습니다.')
    return displayed



# [main3 대비 추가] 성공한 질문/답변 한 쌍을 함께 반영하고 pending을 비웁니다.
def commit_success(state, answer, stats):
    """state: 세션의 대화 상태, answer/stats: 완료 검증을 마친 답변과 측정 결과."""
    pending = state['pending']
    if pending is None or not stats.get('completed') or not answer.strip():
        raise ValueError('완료된 질문과 답변만 성공 기록에 저장할 수 있습니다.')
    saved_stats = {key: value for key, value in stats.items() if key not in ('partial', 'started')}
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


def run_pending(state, min_chars, max_wait, reading_height):
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
        # [main4 대비 추가] height: 읽기 영역 높이(px). 넘치는 내용은 내부 스크롤로 읽습니다.
        with st.container(height=reading_height, border=True):
            answer_box = st.empty()
        try:
            with create_client() as client:
                answer = render_answer(
                    client, inputs, pending['stats'], status, answer_box,
                    fail_after_first=state['fail_next'],
                    min_chars=min_chars, max_wait=max_wait,
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
    st.set_page_config(page_title='요리 AI · 묶음 갱신과 읽기 영역', page_icon='🍳')
    st.title('🍳 요리 AI 어시스턴트')
    st.caption('첫 조각은 바로 표시하고, 이후 조각은 묶어서 고정 높이 영역에 표시합니다.')

    # [main3 대비 추가] 성공 기록과 미완성 질문을 명확히 분리하여 세션에 보관합니다.
    if 'cooking_buffered' not in st.session_state:
        st.session_state.cooking_buffered = {
            'messages': [], 'pending': None, 'fail_next': False, 'notice': '',
        }
    state = st.session_state.cooking_buffered
    pending = state['pending']
    # 설정 변경 등으로 실행이 중단되면 자동 재요청하지 않고 사용자가 재시도를 선택합니다.
    if pending is not None and pending['state'] == 'running':
        pending['state'] = 'failed'
        pending['error'] = '이전 실행이 중단되었습니다. 재시도하거나 취소해주세요.'

    # [main4 대비 추가] 값이 작으면 자주 갱신하고, 크면 더 많은 텍스트를 묶습니다.
    min_chars = st.sidebar.slider('화면 갱신 글자 수', 1, 400, 80, step=1)
    max_wait_ms = st.sidebar.slider('화면 갱신 간격(ms)', 50, 1000, 150, step=50)
    max_wait = max_wait_ms / 1000
    reading_height = st.sidebar.slider('읽기 영역 높이(px)', 200, 500, 400, step=50)
    st.sidebar.caption('첫 조각은 즉시 표시합니다. 이후에는 글자 수 또는 시간 기준으로 갱신하며, 남은 조각은 종료 시 표시합니다.')
    st.sidebar.caption('시간 기준은 새 조각이 도착할 때 확인합니다. 인위적인 sleep은 사용하지 않습니다.')
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
            if message['role'] == 'assistant':
                with st.container(height=reading_height, border=True):
                    st.markdown(message['content'])
            else:
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
                    with st.container(height=reading_height, border=True):
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
            run_pending(state, min_chars, max_wait, reading_height)

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

# 실행: streamlit run day20/main5.py
