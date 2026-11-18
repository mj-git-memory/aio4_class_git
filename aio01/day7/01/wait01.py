# 1. 동기: 지금 작업이 끝나야 다음 작업을 진행
# 2. 비동기: 기다리는 동안 다른 작업을 진행할 수 있음 
#  **“비동기는 대기 시간을 활용하는 방식이고, 여러 작업의 대기를 겹치려면 그 작업들을 함께 진행하도록 등록해야 함”**
# gather()는 그 등록과 결과 수집을 편하게 해주는 방법

# -------------------------------------------------------------
### 1. 동기: 지금 작업이 끝나야 다음 작업을 한다
import time

def make_drink(name):
    print(f'{name} 만들기 시작')
    time.sleep(2)
    print(f'{name} 완성')
    return name

def main():
    make_drink('커피')
    make_drink('차')

main()
## 실행 순서
# 커피 만들기 시작
# (2초 기다림)
# 커피 완성
# 차 만들기 시작
# (2초 기다림)
# 차 완성
# -> 총 약 4초. ime.sleep(2) 동안에는 현재 스레드가 멈춰 있음 


### 2. 비동기: 기다리는 동안 다른 작업을 진행할 수 있다
import asyncio

async def make_drink(name):
    print(f'{name} 만들기 시작')
    await asyncio.sleep(2)
    print(f'{name} 완성')
    return name
# await -> 현재 함수는 결과를 기다리지만, 그동안 이벤트 루프가 다른 준비된 작업을 실행할 수 있다는 뜻


### 3. async def를 사용해도 순서대로 실행할 수 있다
async def main():
    # **“비동기 함수를 순서대로 실행”**
    await make_drink('커피')
    await make_drink('차')
# 1. 커피 작업이 끝날 때까지 기다림
# 2. 그다음 차 작업을 시작
# -> 따라서 총 약 4초가 걸림 
# **“비동기 함수를 순서대로 실행”**
# 비동기 코드이지만, 두 음료 작업을 함께 진행하도록 등록하지 않았기 때문


### 4. gather()를 쓰면 여러 작업을 함께 진행한다
async def main():
    # gather()의 결과는 완료 순서가 아니라 전달한 순서대로 모임 
    result = await asyncio.gather(make_drink('커피'),make_drink('차'))
    print(result)
## 실행 순서
# 커피 만들기 시작
# 차 만들기 시작
# (두 작업이 기다리는 시간을 겹쳐 사용)
# 커피 완성
# 차 완성
# ['커피', '차']
# -> 총 약 2초 걸림


### 5. 꼭 gather()로 묶어야 하나요?
# 아니요. create_task()로 각각 등록할 수도 있습니다.
async def main():
    coffee_task = await asyncio.create_task(make_drink('커피'))
    tea_task =  await asyncio.create_task(make_drink('차'))

    print(coffee_task, tea_task)

asyncio.run(main())
# -> 총 약 2초 걸림
# 여기서는 await를 순서대로 작성했지만, 두 작업을 먼저 등록했기 때문에 커피를 기다리는 동안 차 작업도 진행됨

# # 커피가 끝난 후 차 시작 → 약 4초
# await make_drink('커피')
# await make_drink('차')

# # 두 작업을 먼저 등록하고 결과 기다리기 → 약 2초
# coffee_task = asyncio.create_task(make_drink('커피'))
# tea_task = asyncio.create_task(make_drink('차'))
# await coffee_task
# await tea_task

# async def 함수를 호출하면 코루틴 객체가 만들어짐
# 실행하려면 await로 기다리거나, create_task()·gather() 등으로 실행하도록 등록해야 함

### 6. 언제 사용하나요?
# 비동기는 주로 외부 응답을 기다리는 작업이 여러 개 있을 때 유용
# - 여러 API에 요청하고 응답 기다리기
# - 여러 웹페이지 가져오기
# - 비동기를 지원하는 DB 드라이버로 조회하기
# - 서버에서 여러 사용자 요청 처리하기
# 독립적인 API 요청 3개가 각각 1초씩 걸린다면, 순서대로 처리하면 약 3초지만 함께 진행하면 약 1초에 끝날 수 있음
# 단, 비동기를 지원하는 라이브러리를 사용해야 함. async def 안에 넣었다고 모든 코드가 자동으로 비동기가 되지는 않음


#-------------------------------------------------------------
# 문법	의미
# async def : 비동기 함수 정의
# await : 작업의 완료를 기다리며, 필요하면 다른 작업에 실행 기회를 넘김
# asyncio.run(main()) :	이벤트 루프를 실행해서 비동기 main()을 끝까지 수행
# asyncio.gather(...) :	여러 작업을 함께 진행하고 결과를 모음
# asyncio.create_task(...) : 코루틴을 실행할 작업으로 등록
#-------------------------------------------------------------


print('#-------------------------------------------------------------')
import asyncio
import time 

from time import perf_counter

async def make_drink(name) : # 비동기 작업을 하려면 async def 해줘야 함. 
    print(f'{name} 만들기 시작')
    # time.sleep(2)
    await asyncio.sleep(2) # 비동기로 작업 : 한 작업이 끝날 때까지 기다리지 않고 동시에 진행 
    print(f'{name} 완성')
    return name


async def main() : 
    # 동기식
    start = perf_counter() # 시스템에 현재 시간 정보 저장
    await make_drink('커피')
    # await asyncio.sleep(2)
    await make_drink('차')
    print(f'순서대로 기다림: , {perf_counter() - start :.2f}초\n')

    print('---')
    # 비동기식
    start = perf_counter() # 시스템에 현재 시간 정보 저장
    # 동시에 같이 실행해주고 싶을 때, gather로 모아줘야함
    result = await asyncio.gather(make_drink('커피'), make_drink('차')) 
    print(f'함께 기다림: , {perf_counter() - start :.2f}초\n')
    print('결과', result)

if __name__ == '__main__' : 
    asyncio.run(main())  # 비동기 main()을 실행하기 위해 asyncio.run()을 사용


#---------------------------------------------------------------------------
# if __name__ == "__main__":
#     main()
# **“이 파일을 직접 실행했으면 main()을 호출해라”**라는 뜻

#    *실행 방식* 	     *이 파일 안의 __name__ 값*	    *조건문의 main() 실행*
# python demo.py 	         "__main__"	               실행
# 다른 파일에서 import demo     "demo"                    실행하지 않음 (__name__ =="demo")

#---------------------------------------------------------------------------
