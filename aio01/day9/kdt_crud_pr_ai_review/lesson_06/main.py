def summarize_changes(changes: list[dict]) -> dict:
    return {"changed": [c["path"] for c in changes if c["status"] != "deleted"]}
# summarize_changes: 함수 이름
# changes: 변경 목록을 전달받는 매개변수
# list[dict]: 딕셔너리가 들어 있는 리스트라는 타입 표시
# -> dict: 반환값이 딕셔너리라는 타입 표시

# 여기서 c는 changes 안의 딕셔너리를 하나씩 가리키는 변수
# changes에서 딕셔너리를 하나씩 꺼내요.
# status가 "deleted"가 아닌지 확인해요. !=는 같지 않다는 뜻이에요.
# 조건을 만족하면 path를 새 리스트에 넣어요.


if __name__ == "__main__":
    # 이 조건 안의 코드는 이 파일을 직접 실행했을 때만 실행
    # 다른 파일에서 import하면 실행되지 않음 
    print(summarize_changes([{"path": "old.py", "status": "deleted"}]))
    # 전달한 파일은 "deleted" 상태이므로 목록에서 제외
    # {'changed': []}
