import os 
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import streamlit as st
from dotenv import load_dotenv
from openai import APIError, OpenAI
load_dotenv()

# Groq 모델 생성 함수
def create_client():
    key = os.getenv('GROQ_API_KEY','').strip()
    if not key:
        raise ValueError('.env 파일에 GROQ_API_KEY를 설정해주세요.')
    args = {
        'api_key':key, 'base_url':"https://api.groq.com/openai/v1",
        # timeout: 서버 데이터 수신 대기 제한(초), max_retries: 자동 재시도 횟수
        'timeout':60.0, 'max_retries':0
    }
    return OpenAI(**args)

# 메세지 조합 함수
def build_input(history, question):    
    system_messages = {
        "role": "system",
        "content": """
    너는 여행 계획 및 관광 정보를 전문적으로 제공하는 AI 여행 Agent다.

    [1. 역할과 목적]
    - 사용자의 여행 목적과 요구사항을 분석하고 최적의 여행 정보를 제공한다.
    - 여행지 추천, 관광 명소, 맛집, 숙박, 교통, 여행 경로, 예상 비용, 일정 등을 종합적으로 안내한다.
    - 국내 여행과 해외여행 모두 지원한다.
    - 단순한 정보 나열보다 실제 여행에 활용할 수 있는 구체적이고 실용적인 답변을 제공한다.

    [2. 사용자 입력 분석]
    - 사용자가 제공한 여행 정보를 가장 우선적으로 반영한다.
    - 여행 지역, 여행 기간, 출발지, 인원, 예산, 교통수단, 여행 목적, 선호하는 활동 등을 분석한다.
    - 정보가 충분하지 않더라도 일반적인 여행 패턴과 지역 특성을 바탕으로 합리적인 추천과 추론을 수행한다.
    - 필수 정보가 부족하여 정확한 계획을 수립하기 어려운 경우에만 핵심 내용을 질문한다.
    - 사용자가 명시한 조건과 일반적인 추천 기준이 충돌하면 반드시 사용자 조건을 우선한다.

    [3. 여행지 및 관광 정보]
    - 지역의 대표 관광지, 자연경관, 역사·문화 유적, 체험 활동, 축제 등을 고려한다.
    - 여행자의 연령대, 동행자, 여행 목적에 적합한 장소를 추천한다.
    - 관광지 간 거리와 이동 시간을 고려하여 효율적인 여행 동선을 구성한다.
    - 지역별 특색과 계절적 특성을 반영한다.
    - 실제 존재 여부가 불확실한 장소나 시설을 임의로 만들어내지 않는다.

    [4. 여행 일정 수립]
    - 여행 기간에 맞춰 일자별 일정을 구성한다.
    - 각 일정은 시간대, 방문 장소, 활동 내용, 이동 방법을 포함한다.
    - 불필요한 장거리 이동이나 지나치게 많은 관광지를 포함하지 않는다.
    - 식사, 휴식, 이동 시간을 적절하게 배분한다.
    - 여행지의 운영 시간, 휴무일, 계절별 이용 가능 여부를 고려한다.
    - 사용자의 체력과 여행 스타일에 맞춰 무리하지 않는 일정을 제안한다.

    [5. 교통 및 숙박]
    - 자동차, 대중교통, 도보, 항공, 철도 등 적절한 이동 수단을 고려한다.
    - 이동 거리와 예상 소요 시간을 안내한다.
    - 숙박 장소는 주요 관광지와의 접근성 및 이동 효율성을 고려한다.
    - 숙박비와 교통비는 예산 계획에 포함할 수 있도록 안내한다.
    - 확인되지 않은 요금이나 예약 가능 여부를 확정적으로 표현하지 않는다.

    [6. 맛집 및 음식 추천]
    - 지역을 대표하는 음식과 특산물을 우선적으로 고려한다.
    - 여행 동선과 가까운 식당을 추천한다.
    - 음식 종류, 가격대, 특징 등을 설명한다.
    - 실제 영업 여부나 운영 시간은 확인이 필요한 정보임을 구분한다.
    - 존재하지 않는 식당이나 메뉴를 만들어내지 않는다.

    [7. 예산 및 비용 분석]
    - 교통비, 숙박비, 식비, 입장료, 체험비, 기타 비용을 구분한다.
    - 여행 인원과 기간을 기준으로 예상 비용을 산출한다.
    - 정확한 금액을 확인할 수 없는 경우 합리적인 추정 범위로 제공한다.
    - 실제 가격과 예상 가격을 명확하게 구분한다.
    - 예산이 제한된 경우 비용 대비 만족도가 높은 대안을 추천한다.

    [8. 정보 신뢰성 및 할루시네이션 방지]
    - 검증된 사실과 추론 또는 예상 정보를 구분한다.
    - 실시간 확인이 필요한 항공권, 숙박 예약, 교통편, 날씨, 입장료, 영업시간 등은 확인되지 않은 정보를 사실처럼 답변하지 않는다.
    - 외부 검색이나 API 데이터가 제공되면 해당 데이터를 우선적으로 활용한다.
    - 정보가 없으면 모른다고 명확하게 설명하고 임의로 생성하지 않는다.
    - 과거 정보와 현재 정보가 다를 수 있는 경우 최신 확인이 필요하다고 안내한다.

    [9. 답변 작성 원칙]
    - 기본적으로 한국어로 쉽고 명확하게 답변한다.
    - 결론과 핵심 추천을 먼저 제시한다.
    - 여행 일정은 날짜별 또는 시간대별로 구분한다.
    - 여러 장소를 추천할 때는 추천 이유와 특징을 함께 설명한다.
    - 필요에 따라 표, 목록, 번호 등을 활용한다.
    - 불필요한 반복이나 장황한 설명은 피한다.
    - 사용자가 간단한 답변을 요청하면 핵심 내용만 제공한다.
    - 사용자가 상세한 계획을 요청하면 충분한 설명과 구체적인 정보를 제공한다.

    [10. 최종 목표]
    사용자가 별도의 여행 전문가 도움 없이도 실제 여행 계획을 세울 수 있도록 정확하고 실용적이며 실행 가능한 여행 정보를 제공한다.
    """    
    }
    return [system_messages] + history + [{"role":"user", "content":question}]

# 스트리밍으로 시간을 측정하고, 완성된 답변을 한 번에 반환합니다.
def render_answer(client, inputs, stats):
    """client: API 연결, inputs: 대화 메시지 목록, stats: 측정 결과를 저장할 사전."""
    started = time.perf_counter()
    completed = False
    stats.update(first=None, total=None, partial='', updates=0, completed=False)
    try:
        with client.responses.create(
            model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b').strip(),
            input=inputs,  # 시스템 지침 + 이전 대화 + 이번 질문
            stream=True,  # 첫 텍스트 도착 시점을 알기 위해 이벤트 단위로 수신
            store=False,  # 대화 기록은 Streamlit 세션에서 관리
        ) as stream:
            for event in stream:
                if event.type == 'response.output_text.delta' and event.delta:
                    # 연결/상태 이벤트가 아닌, 실제 답변 텍스트가 처음 도착한 시간
                    if stats['first'] is None:
                        stats['first'] = time.perf_counter() - started
                    stats['partial'] += event.delta
                    stats['updates'] += 1
                elif event.type == 'response.completed':
                    stats['total'] = time.perf_counter() - started
                    completed = True
                    break
                elif event.type in ('response.failed', 'response.incomplete', 'error'):
                    raise ValueError('서버에서 답변 생성을 완료하지 못했습니다. 다시 시도해주세요.')

        if not completed:
            raise ValueError('답변 수신 중 연결이 종료되었습니다. 다시 시도해주세요.')
        if not stats['partial'].strip():
            raise ValueError('답변 텍스트가 비어 있습니다. 다시 질문해주세요.')
        stats['completed'] = True
        return stats['partial']
    finally:
        # 실패한 요청도 종료까지 걸린 시간을 기록합니다.
        if stats['total'] is None:
            stats['total'] = time.perf_counter() - started


# 메인함수 UX (streamlit)
def main():
    st.set_page_config(page_title='AI 여행 도우미', page_icon='✈️')
    st.title('✈️ AI 여행 도우미')
    st.caption('여행지, 기간, 예산을 알려주시면 여행 계획을 도와드립니다.')

    # value: 기본값, min/max_value: 설정 범위, step: 한 번에 바꿀 초 단위
    wait_seconds = st.sidebar.number_input(
        '긴 응답 대기 안내 기준(초)',
        min_value=1.0, max_value=60.0, value=5.0, step=1.0,
        help='이 시간을 넘겨도 답변이 완료되지 않으면 대기 안내를 변경합니다.',
    )

    # Streamlit 재실행 후에도 사용자별 세션에 대화와 측정 결과를 유지합니다.
    if 'travel_messages' not in st.session_state:
        st.session_state.travel_messages = []

    for message in st.session_state.travel_messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            if 'timing' in message:
                st.caption(message['timing'])

    question = st.chat_input(placeholder='예: 부산 2박 3일, 2명, 예산 50만 원으로 계획해줘')
    if not question or not question.strip():
        return
    question = question.strip()

    with st.chat_message('user'):
        st.markdown(question)

    # 화면 표시용 timing은 제외하고 API가 받는 role/content만 전달합니다.
    history = [
        {'role': message['role'], 'content': message['content']}
        for message in st.session_state.travel_messages
    ]
    # history: 이전 대화, question: 이번 질문. 현재 질문이 중복되지 않게 조합합니다.
    inputs = build_input(history, question)
    stats = {}

    with st.chat_message('assistant'):
        notice = st.empty()
        notice.info('여행 답변을 준비하고 있어요...')
        try:
            with create_client() as client:
                # API 수신만 작업 스레드에서 처리하고, 화면 표시는 main에서 수행합니다.
                with ThreadPoolExecutor(max_workers=1) as executor:
                    # 요청은 한 번만 실행합니다. future는 그 요청의 작업 결과입니다.
                    future = executor.submit(render_answer, client, inputs, stats)
                    try:
                        # timeout: 이 시간까지 기다린 뒤 대기 안내만 변경합니다.
                        answer = future.result(timeout=wait_seconds)
                    except FutureTimeoutError:
                        notice.info(
                            f'{wait_seconds:g}초가 지났습니다. 답변을 계속 준비하고 있어요. '
                            '완료되면 한 번에 표시합니다.'
                        )
                        answer = future.result()  # 새 요청 없이 같은 작업의 완료를 대기
        except (APIError, ValueError) as error:
            notice.empty()
            if isinstance(error, APIError):
                st.error('API 요청에 실패했습니다. 키, 모델명, 사용 한도와 네트워크를 확인해주세요.')
            else:
                st.error(str(error))
            # 중간까지 받은 답변은 성공한 대화로 저장하지 않습니다.
            if stats.get('total') is not None:
                first = stats.get('first')
                first_text = f'{first:.2f}초' if first is not None else '수신하지 못함'
                st.caption(
                    f"첫 텍스트 수신: {first_text} · 실패까지: {stats['total']:.2f}초"
                )
            return

        notice.empty()
        # first와 total 모두 render_answer 내부의 같은 started를 기준으로 측정합니다.
        response_kind = '짧은 응답' if stats['total'] <= wait_seconds else '긴 응답'
        timing = (
            f"첫 텍스트 수신: {stats['first']:.2f}초 · "
            f"전체 응답: {stats['total']:.2f}초 · "
            f"{response_kind}(기준 {wait_seconds:g}초)"
        )
        st.markdown(answer)
        st.caption(timing)

    # 성공한 질문/답변만 함께 저장하고, 측정 결과도 재실행 후 다시 표시합니다.
    st.session_state.travel_messages.extend([
        {'role': 'user', 'content': question},
        {'role': 'assistant', 'content': answer, 'timing': timing},
    ])


if __name__ == '__main__':
    main()


# streamlit run day20/main2.py # 로 실행 