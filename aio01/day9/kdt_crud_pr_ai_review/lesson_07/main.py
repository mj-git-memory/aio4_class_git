def can_edit(role: str) -> bool:
    return "admin" in role
    # 문자열에서 in은 해당 글자가 포함되어 있는지 검사

if __name__ == "__main__":
    print(can_edit("not-admin"))

# can_edit: 함수 이름으로, “수정할 수 있는가?”라는 뜻
# role: 역할을 전달받는 매개변수
# str: 입력이 문자열이라는 타입 표시
# -> bool: True 또는 False를 반환한다는 타입 표시 