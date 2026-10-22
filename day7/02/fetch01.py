import asyncio
import os
import sys
import httpx

BASE_URL = 'https://jsonplaceholder.typicode.com'


async def main(todo_id) : 
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=10.0
    ) as client : 
        response = await client.get(f'/posts/{todo_id}')
        # -> <Response [200 OK]> <class 'httpx.Response'> : Resoponse라는 객체 생성
        print(response, type(response), response.json())
        # -> {'userId': 1, 'id': 1, 'title': 'sunt aut facere repellat provident occaecati excepturi optio reprehenderit', 'body': 'quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto'}
        jsondata = response.json()
        print("\n", jsondata['title'])
        # -> sunt aut facere repellat provident occaecati excepturi optio reprehenderit

if __name__ == '__main__' :
    asyncio.run(main(1))

# <Response [200 OK]> <class 'httpx.Response'> # -> Resoponse라는 객체 생성
# 200 : 성공
# 404 : 페이지 없음 (요청 주소가 잘못됐을 때)