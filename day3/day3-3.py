### 2. 실습 예제 8-1: AI 점수 정규화 파이프라인 Before & After 캡스톤 코드
# [Before: 리팩토링 전 — 이상치·결측치 유입 시 즉시 크래시되는 취약한 함수]
def preprocess_legacy(data):
    res = []
    for row in data:
        # 치명적 결함: 'score' 키가 없거나 'N/A' 문자열이면 즉시 프로그램 강제 종료!
        # 치명적 결함: 100점을 초과하는 이상치(120점)도 걸러내지 못하고 1.2로 잘못 정규화함!
        score = float(row["score"])
        res.append(round(score / 100.0, 4))
    return res

# preprocess_legacy(50)
preprocess_legacy(150)
