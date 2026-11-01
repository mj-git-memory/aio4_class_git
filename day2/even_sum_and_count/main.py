### 1부터 입력한 숫자 n까지의 짝수 합과 개수를 구하고, 함수가 올바르게 동작하는지 테스트하는 코드

## 1. 함수 정의와 변수 초기화
def calculate_even_sum_and_count(n): # n: 계산할 범위의 마지막 숫자
    """1부터 n까지의 짝수 합과 개수를 반환한다.""" # 함수의 역할을 설명하는 문자열인 **독스트링(docstring)**
    even_sum = 0 # even_sum: 짝수의 합을 저장
    even_count = 0 # even_sum: 짝수의 합을 저장
    # -> 두 변수는 함수 안에 있으므로 호출할 때마다 0으로 시작

    ## 2. 1보다 작은 입력 처리
    if n < 1:
        return {"Sum": 0, "Count": 0}
        # -> n이 0이나 음수이면 계산할 대상이 없다고 보고, 합과 개수를 모두 0으로 반환
        # return이 실행되면 함수가 종료되므로 아래 반복문은 실행되지 않음 

    ## 3. 짝수의 합과 개수 계산
    for i in range(1, n + 1): # range()는 끝 숫자를 포함하지 않으므로, **n까지 포함하려고 n + 1**을 사용
        if i % 2 == 0: # i % 2 == 0은 2로 나눈 나머지가 0인지, 즉 짝수인지 확인
            even_sum += i
            even_count += 1

    ## 4. 결과를 딕셔너리로 반환
    return {"Sum": even_sum, "Count": even_count}


if __name__ == "__main__": # 현재 파일을 직접 실행했을 때만 실행. 다른 파일에서 import하면 실행되지 않음 
    import json 

    n = int(input("정수 n을 입력하세요: "))
    print(json.dumps(calculate_even_sum_and_count(n))) 
    # -> # json.dumps()로 반환된 딕셔너리를 JSON 형식의 문자열로 바꿈

    ## assert는 조건이 참인지 확인하는 검증문
    ## assert 조건, "조건이 거짓일 때 표시할 메시지"
    # -> 조건이 참이면 아무것도 출력하지 않고 다음 줄로 넘어감 
    # -> 조건이 거짓이면 AssertionError가 발생하며 실행이 중단
    assert calculate_even_sum_and_count(100) == {"Sum": 2550, "Count": 50}, 'Test 1 Failed'
    assert calculate_even_sum_and_count(1) == {"Sum": 0, "Count": 0}, 'Test 2 Failed'
    assert calculate_even_sum_and_count(-5) == {"Sum": 0, "Count": 0}, 'Test 3 Failed'
    assert calculate_even_sum_and_count(-5) == {"Sum": 0, "Count": 1}, 'Test 4 Failed'
    # -> AssertionError: Test 4 Failed
    print('모든 케이스가 성공했습니다.')
