def is_ready(value: str) -> bool:
    return bool(value)

if __name__ == "__main__":
    print(is_ready("false")) # 문자열이 입력되어 있으면 True
    print(is_ready(bool(0))) # 0은 False 의미
    print(is_ready(bool(-1))) # 0은 False 의미
