# llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF --alias local-chat  # 터미널에서 실행
# -> 이 명령어는 **“Qwen 모델을 내려받아 내 컴퓨터에서 실행하고, local-chat이라는 이름으로 요청받을 준비를 해라”**라는 뜻
# -> 처음 실행하면 필요한 모델을 다운로드하고, 이후에는 저장된 파일을 재사용
# -> 서버는 Streamlit 같은 프로그램에서 보낸 질문을 받아 답변을 생성

import os
from dotenv import load_dotenv

import requests
import streamlit as st

load_dotenv()
base_url = os.getenv('LLAMA_BASE_URL', '').strip()
model = os.getenv('LLAMA_MODEL', '').strip()
timeout_text = os.getenv('LLMA_TIMEOUT_SECONDS', '180').strip()
timeout_seconds = int(timeout_text)


name = st.text_input('이름')
question = st.text_input('질문')

with st.chat_message('user') : 
    st.text(f'{name} : {question}')

headers={}
if st.button('ai 답변 받기') :  # st.button()은 버튼을 클릭한 실행에서만 True를 반환
    with st.spinner('ai가 답변을 생성하고 있습니다.') : 
        with requests.post(
            f'{base_url}/v1/chat/completions', # 채팅 api 주소
            headers= headers,
            json = {
                'model':model, # 서버의 --alias와 일치하는 모델
                'messages': [
                    {'role':'system', 'content':'한국어로 쉽고 간결하게 답하세요. 핵심만 2~3문장으로 답하세요.'},
                    {'role':'user', 'content':question},
                ],
                'temperature':0.7, # 답변 선택의 무작위성. 추론량이나 속도를 조절하는 값은 아님
                'chat_template_kwargs': {'enable_thinking': False}, # 별도의 thinking 모드 끄기
                'max_tokens':128, # 생성 토큰 수 상한. 너무 길면 답변이 중간에 끊길 수 있음
                'stream':False # 토큰 별 스트리밍 대신 json 수신
            },
            timeout=(5,timeout_seconds)
        ) as response : 
            response.raise_for_status()
            data = response.json() # 객체로 복원

        choice = data['choices'][0]
        answer = choice['message']['content']
        with st.chat_message('assistant'):
            st.text(answer.strip())


