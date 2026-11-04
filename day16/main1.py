# Streamlit : Python 코드로 데이터와 AI 기능을 웹 화면에 보여 주는 오픈소스 프레임워크
# -> HTML, CSS, JavaScript를 직접 작성하지 않아도 버튼, 입력창, 표, 그래프가 있는 웹 앱을 만들 수 있음
# -> 데이터 분석 화면, 머신러닝 예측 도구, AI 챗봇 등에 활용할 수 있음 

import streamlit as st
st.title('ui 실습')
st.caption('입력 -> 공백 검사 -> 대화내용 미리 보기')
st.write('안녕하세요!')

name = st.text_input('이름', placeholder='ex) 민수')
print(name)
question = st.text_input('질문', placeholder='ex) streamlit은 무엇인가요?')

show_hint = st.checkbox('실행원리 설명 보기')
if show_hint : 
    st.info('체크하면 보이지롱~~~')

if st.button('대화 미리보기') :  # st.button()은 버튼을 클릭한 실행에서만 True를 반환
    clean_name = name.strip()  # .strip() : 양 끝의 공백을 제거. 중간의 공백은 유지
    clean_question = question.strip()

    if not clean_name or not clean_question :
        st.warning('이름과 질문을 모두 입력하세요.')
    else :
        with st.chat_message('user') : 
            st.text(f'{clean_name} : {clean_question}')
        with st.chat_message('assistant') : 
            st.text(f'{clean_name}님 질문을 확인했습니다. 이 화면은 미리보기 입니다.')
else :  # 처음 화면을 열거나, 다른 입력값을 바꿔 실행됐을 때 → False
    st.caption('이름과 질문을 입력한 뒤 미리보기 버튼을 누르세요.')

# python -m pip install streamlit  # 설치
# python -m streamlit run main1.py  # 터미널에서 실행