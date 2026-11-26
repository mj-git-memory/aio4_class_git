## s2는 “외부 REST API를 호출하는 클라이언트”
# s2 실행 구조

# s2: 게시글 데이터 준비
#     ↓ HTTP POST 요청
# 외부 JSONPlaceholder API
#     ↓ HTTP 응답
# s2: 응답 내용을 읽고 출력

# https://jsonplaceholder.typicode.com/

## s2: 외부 REST API에 데이터 보내기
import requests 
def test_rest_api() : 
    base_url = 'https://jsonplaceholder.typicode.com'
    endpoint = f'{base_url}/posts'
    payload = {
        'title':'window VScode api Test',
        'body':'Postman과 python 3.13을 활용한 외부 api 호출',
        'userId':1
    }
    header = {'Content-Type':'application/json; charset=UTF-8'} # 데이터 형식을 알려주는 헤더
    # -> “요청 본문은 JSON이며 UTF-8 인코딩을 사용합니다.” 라는 뜻
    # api 요청
    response = requests.post(endpoint, json=payload, headers=header, timeout=10) # 반환값은 딕셔너리가 아니라 Response 객체
    # endpoint : 요청할 URL / json=payload : 딕셔너리를 JSON 본문으로 전송
    # headers=header : 요청에 붙일 부가 정보 / timeout=10 : 연결·읽기 대기에 사용할 타임아웃 설정
    print(f'http status: {response.status_code}')
    data = response.json()
    print('응답본문', data)
    print(f'생성된 id: {data.get('id')}')

if __name__ == '__main__':
    test_rest_api()

# npm install -g postman-cli
# request POST https://jsonplaceholder.typicode.com/posts