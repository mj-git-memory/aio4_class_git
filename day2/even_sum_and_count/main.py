def calculate_even_sum_and_count(n):
    """1부터 n까지의 짝수 합과 개수를 반환한다."""
    even_sum = 0
    even_count = 0

    if n < 1:
        return {"Sum": 0, "Count": 0}

    for i in range(1, n + 1):
        if i % 2 == 0:
            even_sum += i
            even_count += 1

    return {"Sum": even_sum, "Count": even_count}


if __name__ == "__main__":
    import json

    n = int(input("정수 n을 입력하세요: "))
    print(json.dumps(calculate_even_sum_and_count(n)))

    assert calculate_even_sum_and_count(100) == {"Sum": 2550, "Count": 50}, 'Test 1 Failed'
    assert calculate_even_sum_and_count(1) == {"Sum": 0, "Count": 0}, 'Test 2 Failed'
    # assert calculate_even_sum_and_count(-5) == {"Sum": 0, "Count": 1}, 'Test 3 Failed'
    assert calculate_even_sum_and_count(-5) == {"Sum": 0, "Count": 0}, 'Test 3 Failed'
    print('모든 케이스가 성공했습니다.')
