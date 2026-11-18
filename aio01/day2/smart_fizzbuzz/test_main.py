### analyze_fizzbuzz() 함수가 여러 입력에 대해 올바른 결과를 반환하는지 확인하는 테스트 코드

## 1. 검사할 함수 가져오기
from main import analyze_fizzbuzz # main.py에 정의된 analyze_fizzbuzz 함수를 가져옴 

# | 분류         | 의미                        |
# |---          |---                         |
# | `FizzBuzz`  | 3과 5의 공배수                |
# | `Fizz`      | 3의 배수이면서 5의 배수는 아닌 수 |
# | `Buzz`      | 5의 배수이면서 3의 배수는 아닌 수 |
# | `Number`    | 3의 배수도, 5의 배수도 아닌 수   |

## 2. 테스트 데이터 준비
def test_analyze_fizzbuzz():
    cases = [
        (-5, {"FizzBuzz": 0, "Fizz": 0, "Buzz": 0, "Number": 0}),
        (0, {"FizzBuzz": 0, "Fizz": 0, "Buzz": 0, "Number": 0}),
        (1, {"FizzBuzz": 0, "Fizz": 0, "Buzz": 0, "Number": 1}),
        (3, {"FizzBuzz": 0, "Fizz": 1, "Buzz": 0, "Number": 2}),
        (5, {"FizzBuzz": 0, "Fizz": 1, "Buzz": 1, "Number": 3}),
        (15, {"FizzBuzz": 1, "Fizz": 4, "Buzz": 2, "Number": 8}),
        (30, {"FizzBuzz": 2, "Fizz": 8, "Buzz": 4, "Number": 16}),
    ]
    # -> cases는 입력값과 예상 결과를 튜플로 묶어 저장한 리스트

    ## 3. 입력값과 예상 결과 꺼내기
    for limit, expected in cases: # 언패킹. 각 튜플의 두 값을 나누어 받음
        actual = analyze_fizzbuzz(limit) # 함수를 실행한 실제 결과를 actual에 저장

        ## 4. 세 가지 조건 검사하기
        # ① 실제 결과가 예상 결과와 같은가?
        assert actual == expected, f"limit={limit}: {actual} != {expected}"
        # -> 같으면 다음 줄로 넘어감
        # -> 다르면 AssertionError가 발생하고, 쉼표 뒤의 메시지가 표시
        
        # ② 모든 개수가 정수인가?
        assert all(type(count) is int for count in actual.values()) 
        # -> actual.values() : 딕셔너리의 값들 
        # -> type(count) is int : 값의 자료형이 정확히 int인지 확인
        # -> all(...) : 검사 결과가 모두 참인지 확인 ex)값이 1, 4, 2, 8이면 모두 정수이므로 통과
        
        # ③ 분류별 개수를 더하면 전체 숫자 개수와 같은가?
        assert sum(actual.values()) == max(0, limit) # max(0, limit)을 사용하면 음수일 때 기대하는 개수를 0으로 처리
        # -> sum(actual.values()): 네 분류의 개수를 모두 더함
        # -> max(0, limit): 0과 limit 중 큰 값을 선택
        
        print(f"limit={limit}: 통과")
        print(actual.values())
        print(max(0, limit))


if __name__ == "__main__": # 이 파일을 직접 실행하면 테스트 함수가 실행
    test_analyze_fizzbuzz()
    print("모든 테스트 통과") # 중간에 하나라도 실패하면 오류가 발생해 실행이 중단되므로, 마지막 메시지는 출력되지 않음 
