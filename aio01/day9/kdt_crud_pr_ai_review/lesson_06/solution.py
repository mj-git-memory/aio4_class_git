def summarize_changes(changes: list[dict]) -> dict:
    return {"changed": [c["path"] for c in changes]}
    # [c["path"] for c in changes]는 changes에서 딕셔너리를 하나씩 꺼내서 "path" 값만 모으는 코드
    # 삭제 여부와 관계없이, 변경 목록에 있는 모든 파일의 경로를 모아 반환

if __name__ == "__main__":
    print(summarize_changes([{"path": "old.py", "status": "deleted"}]))
    # {'changed': ['old.py']}