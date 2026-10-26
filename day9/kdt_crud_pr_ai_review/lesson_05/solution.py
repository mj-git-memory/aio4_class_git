def is_ready(value: str) -> bool:
    return value.lower() == "true"
    # .lower()로 소문자로 바꾼 뒤, 문자열이 "true"와 같은지 비교

if __name__ == "__main__":
    print(is_ready("false"))
