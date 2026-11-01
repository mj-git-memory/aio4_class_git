# 리스트 컴프리핸션

result = []
list_1 = [1,2,3,4,5]

for i in list_1 : 
    if i % 2 == 0 :
        result.append(i)
print(result)

result2 = [i for i in list_1 if i%2 == 0]
print(result2)
print('-------')


result = []
for i in list_1 :
    if i > 3 : 
        result.append(i*2)
print(result)

result3 = [i*2 for i in list_1 if i >3 ]
print(result3)
print('-------')


menu = ['아메리카노', '라떼', '초코']
ice_menu = ["ice_" + i for i in menu]
print(ice_menu)

len_menu = [f'{i}-{len(i)}글자' for i in menu if len(i)%2 == 0]
# -> [for i in 집합 if '참']
print(len_menu)
print('-------')


ages = [20, 15, 60, 25, 30, 45, 5]
print([i for i in ages if i >= 20])
print(['성인' if i >= 20 else '미성년' for i in ages])
# -> # ['참' if 조건 else '거짓' for i in 집합]
print('-------')


if ' ' : # true - 공백도  true
    print('abc')
if '' : # flase - 빈 문자열은 false
    print('abc')
print('-------')



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

### 금지어 목록을 정리한 뒤, 채팅 메시지에 있는 금지어를 글자 수만큼 *로 바꾸는 코드

## 1. 빈 문자열과 중복을 제거하고 길이순으로 정렬
bad_words = ['바보', '멍청이', '멍텅구리', '', '바보']
words = sorted(set(word for word in bad_words if word), key=len, reverse=True)
# word for word in bad_words if word
# -> word를 하나씩 꺼내서, 참으로 평가되는 값만 남김 
# for word in bad_words	: 단어를 하나씩 꺼냄
# if word :	빈 문자열 ''을 제외
# set(...) : 중복된 '바보' 제거
# sorted(..., key=len) : 글자 수를 기준으로 정렬
# reverse=True : 긴 단어부터 정렬
print(words) # ['멍텅구리', '멍청이', '바보']

## 2. 정규표현식 패턴 만들기
import re  # 문자열에서 특정 패턴을 찾거나 바꾸는 정규표현식 모듈을 가져옴 
print("|".join(re.escape(word) for word in words))  # 멍텅구리|멍청이|바보
# re.escape(word): 단어에 정규표현식 특수문자가 있으면 일반 문자로 검색되도록 처리. 
# -> 예를 들어 a.b의 .을 “아무 문자”가 아닌 실제 마침표로 찾게 함 
# "|".join(...): 단어 사이에 |를 넣어 하나의 문자열로 연결
print(type("|".join(re.escape(word) for word in words)))  # <class 'str'>

pattern = "|".join(re.escape(word) for word in words)

## 3. 찾은 금지어를 *로 바꾸기
chat_message = '철수는 바보가 맞습니다.'
filtered_message = re.sub(pattern, lambda match: "*" * len(match.group(0)),
                  chat_message, flags=re.IGNORECASE)
# re.sub(찾을_패턴, 바꿀_내용, 원본_문자열)
# 바꿀 내용을 함수로 지정 : lambda match: "*" * len(match.group(0))
# -> 부분              	이번 예제의 값
# -> match.group(0)	    발견된 전체 문자열인 '바보'
# -> len(match.group(0))	글자 수 2
# -> "*" * 2           	'**'
# ags=re.IGNORECASE : 영문 대소문자를 구분하지 않고 검색하는 옵션

print(chat_message)      # 철수는 바보가 맞습니다.
print(filtered_message)  # 철수는 **가 맞습니다.



# 1. re.escape(word)가 필요한 이유
# 정규표현식에서는 일부 문자가 특별한 의미를 가집니다. 예를 들어 **.은 “아무 문자 한 개”**를 뜻합니다.
# import re

# print(re.findall("a.b", "a.b aXb a1b"))
# # ['a.b', 'aXb', 'a1b']
# "a.b"를 찾으라고 했지만, .이 아무 문자와 일치하므로 "aXb", "a1b"도 찾아집니다.

# 실제 글자 그대로 "a.b"만 찾고 싶을 때 re.escape()를 사용합니다.
# pattern = re.escape("a.b")

# print(pattern)  # a\.b

# print(re.findall(pattern, "a.b aXb a1b"))
# # ['a.b']
# 여기서 \.은 “특별한 의미 없이 실제 마침표를 찾아라”라는 뜻입니다.

# 현재 금지어인 "바보", "멍청이"에는 이런 특수문자가 없으므로 re.escape()를 적용해도 그대로입니다.
# 2. re.sub()는 찾은 문자열을 바꿉니다
# 먼저 간단한 형태를 보면:
# result = re.sub("바보", "**", "철수는 바보가 맞습니다.")
# print(result)
# # 철수는 **가 맞습니다.
# 구조는 다음과 같습니다.
# re.sub(찾을_패턴, 바꿀_내용, 원본_문자열)
# 그런데 금지어마다 길이가 다르면 **로 고정해서 바꾸는 대신, 찾은 단어의 길이만큼 별표를 만들어야 합니다.
# 바보     → **
# 멍청이   → ***
# 멍텅구리 → ****
# 그 작업을 하는 부분이 다음 코드입니다.
# lambda match: "*" * len(match.group(0))
# lambda는 이름 없이 짧게 만드는 함수입니다. 위 코드는 아래 함수와 같은 역할입니다.
# def replace_word(match):
#     found_word = match.group(0)  # 실제로 찾은 단어
#     length = len(found_word)    # 그 단어의 글자 수
#     return "*" * length        # 글자 수만큼 별표 반환
# re.sub()는 단어를 찾을 때마다 이 함수를 호출하고, 함수가 반환한 별표로 그 단어를 바꿉니다. 
# match는 re.sub()가 자동으로 전달합니다.

# 따라서 원래 코드는 다음처럼 풀어 쓸 수 있습니다.
# import re

# pattern = "바보|멍청이"
# chat_message = "바보, 멍청이라고 부르지 마세요."

# def replace_word(match):
#     found_word = match.group(0)
#     return "*" * len(found_word)

# filtered_message = re.sub(
#     pattern,
#     replace_word,
#     chat_message,
#     flags=re.IGNORECASE
# )

# print(filtered_message)
# # **, ***라고 부르지 마세요.
# 마지막의 flags=re.IGNORECASE는 영문 대소문자를 구분하지 않는 옵션입니다. 
# 예를 들어 패턴이 "bad"여도 "BAD", "Bad"까지 찾습니다. 현재 한글 예제에는 영향을 주지 않습니다.