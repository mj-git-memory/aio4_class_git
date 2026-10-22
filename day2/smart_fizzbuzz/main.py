def analyze_fizzbuzz(limit: int) -> dict:
    """1부터 limit까지 숫자를 FizzBuzz 규칙으로 분류해 개수를 반환한다."""
    counts = {"FizzBuzz": 0, "Fizz": 0, "Buzz": 0, "Number": 0}

    if limit < 1:
        return counts

    for i in range(1, limit + 1):
        if i % 3 == 0 and i % 5 == 0:
            counts["FizzBuzz"] += 1
        elif i % 3 == 0:
            counts["Fizz"] += 1
        elif i % 5 == 0:
            counts["Buzz"] += 1
        else:
            counts["Number"] += 1

    return counts


if __name__ == "__main__":
    limit = int(input("정수 limit를 입력하세요: "))
    print(analyze_fizzbuzz(limit))
