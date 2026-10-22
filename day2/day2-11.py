# 리스트 컴프리핸션

result = []
list_1 = [1,2,3,4,5]

for i in list_1 : 
    if i % 2 == 0 :
        result.append(i)

print(result)

result2 = [i for i in list_1 if i%2 == 0]
print(result2)


for i in list_1 :
    result.append(i*2)

result3 = [i*2 for i in list_1 if i >3 ]
print(result3)


menu = ['아메리카노', '라떼', '초코']
ice_menu = ["ice_" + i for i in menu]
print(ice_menu)
len_menu = [len(i) for i in menu if len(i)%2 == 0]
print(len_menu)

# ['참' if 조건 else '거짓' for i in 집합]
# [for i in 집합 if '참']

ages = [20, 15, 60, 25, 30, 45, 5]
print([i for i in ages if i >= 20])
print(['성인' if i >= 20 else '미성년' for i in ages])

# if '' : # flase - 빈 문자열은 false
if ' ' : # true - 공백도  true
    print('abc')



# R I O C
# Role
# Input
# Output
# Constraints

'''
[Role]
너는 온라인 게임 채팅 시스템의 백엔드 파이썬 개발자야.

[Task]
채팅 메시지에서 금지 단어를 찾아 마스킹(*) 처리하는 함수를 작성해줘.

[Input]
1. chat_message (str): 사용자가 입력한 채팅 메시지
2. bad_words (list[str]): 금지 단어 목록

[Output]
- masked_message (str): 금지어가 '*'로 치환된 최종 문자열

[Constraints & Logic]
- 함수명: mask_bad_words(chat_message: str, bad_words: list[str]) -> str
- 금지 단어의 글자 수만큼 '*'로 치환할 것 (예: "바보" -> "**")
- 대소문자를 구분하지 않고 찾되, 원본 메시지의 다른 문장 구조는 그대로 보존할 것
- 주석으로 각 핵심 라인이 어떻게 동작하는지 초보자도 알기 쉽게 달아줄 것
- 생성된 코드는 대중적으로 해석하기 쉬운 기본 문법과 라이브러리만을 사용할 것
- 생성된 코드는 오류가 없는지 확인할 것
- 예측가능한 테스트케이스를 (assert 사용) 다양하게 만들고 실행해서 오류가 있으면 수정할 것
'''

bad_words = ['바보', '멍청이', '멍텅구리', '', '바보']
words = sorted(set(word for word in bad_words if word), key=len, reverse=True)
print(words)

import re 
print("|".join(re.escape(word) for word in words))
print(type("|".join(re.escape(word) for word in words)))
pattern = "|".join(re.escape(word) for word in words)

chat_message = '철수는 바보가 맞습니다.'
re.sub(pattern, lambda match: "*" * len(match.group(0)),
                  chat_message, flags=re.IGNORECASE)


