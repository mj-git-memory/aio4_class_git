# What : 무엇을 만들지 
# Constraints : 어떤 제약으로 동작해야 하는지
# How : 구현은 어떻게 (어떻게 동작해야 하는지)
# Vibe Check : 결과를 검증
# 3대 핵심 룰 P(Prompt) -> G(Generator) -> V(Validator)
# P(Prompt) : 입력(input), 출력(output), 알고리즘 제약 조건, 함수 명시
# Validator : 결과 검증 

### Ex)
# 1부터 N까지의 짝수 합과 개수 구하기
# Bed : 짝수 합 구해줘
'''
[Problem] 1부터 n까지의 정수 중 짝수들의 합과 짝수의 총 개수를 계산
[Function] calculate_even_sum_and_count(n)
[Rules]
    - n이 1 미만인 경우 합 0, 개수 0을 반환
    - for 문과 if 문을 활용하여 짝수 (i%2 ==0)를 판단
[Output] {"Sum":int, "Count":int}
'''
# --> even_sum_and_count 파일


### 실습 규칙
'''
문제 정의 / 입력값 / 출력값 / 제약조건을 작성
assert 함수를 활용하여 테스트 케이스 작성 


[Mission 1: Smart FizzBuzz Analyzer]
- 함수명: analyze_fizzbuzz(limit: int) -> dict
- 로직 제약:
  1. 1부터 limit까지 순회한다.
  2. 3의 배수이면서 5의 배수이면: "FizzBuzz" 카운트 증가
  3. 3의 배수이면: "Fizz" 카운트 증가
  4. 5의 배수이면: "Buzz" 카운트 증가
  5. 그 외의 숫자이면: "Number" 카운트 증가
- 반환값 형식:
  {"FizzBuzz": int, "Fizz": int, "Buzz": int, "Number": int}
- 엣지 케이스: limit가 1 미만인 경우 모든 카운트가 0인 딕셔너리 반환
'''
# --> smart_fizzbuzz 파일 