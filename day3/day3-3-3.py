# 2. 실습 예제 8-1: AI 점수 정규화 파이프라인 Before & After 캡스톤 코드

## 여러 행의 점수를 검사해서 정상 점수는 0~1 사이로 정규화하고, 잘못된 행은 제외 이유를 기록
# 데이터 입력
# → 점수 존재 여부 검사
# → 숫자 변환
# → 허용 범위 검사
# → 정상이면 정규화 / 오류면 제외 사유 기록
# → 결과 보고서 반환

# [Before: 리팩토링 전 — 이상치·결측치 유입 시 즉시 크래시되는 취약한 함수]
## 1. preprocess_legacy() — 개선 전 전처리 함수
# -> 키 누락이나 변환 오류를 처리하지 않고, 범위도 검사하지 않음 
# {"score": "N/A"}	ValueError
# {}	KeyError

def preprocess_legacy(data):
    res = []
    for row in data:
        # 치명적 결함: 'score' 키가 없거나 'N/A' 문자열이면 즉시 프로그램 강제 종료!
        # 치명적 결함: 100점을 초과하는 이상치(120점)도 걸러내지 못하고 1.2로 잘못 정규화함!
        score = float(row["score"])
        res.append(round(score / 100.0, 4))
    return res


# [After: Codex 방어적 리팩토링 후 — 검증 캡슐화 + 예외 체이닝 + 자동 성공률 리포트]
from dataclasses import dataclass

## 2. DataValidationError — 검증 실패를 나타내는 예외
# -> 점수 누락·변환 실패·범위 초과를 하나의 예외 종류로 묶음. 호출하는 쪽은 이 예외를 잡아 잘못된 행을 처리할 수 있음
class DataValidationError(Exception):
    """데이터 전처리 검증 실패를 나타내는 커스텀 예외"""
    pass

## 3. PreprocessReport — 결과를 담는 데이터클래스
@dataclass
class PreprocessReport:
    normalized_scores: list[float] # 정상 점수의 정규화 결과
    skipped_rows: list[str] # 제외한 행 번호와 이유

    @property
    def success_rate(self) -> float:  # success_rate는 조회할 때 성공률을 계산하는 프로퍼티
        total = len(self.normalized_scores) + len(self.skipped_rows)
        return round((len(self.normalized_scores) / total) * 100, 1) if total > 0 else 0.0 # 성공률 = 정상 건수 ÷ 전체 건수 × 100
    
class SafeScorePreprocessor:
    ## 4. __init__() — 점수 범위 설정
    def __init__(self, min_score: float = 0.0, max_score: float = 100.0): # 허용 범위를 0~100으로 설정
        if max_score <= min_score:
            raise ValueError("max_score는 min_score보다 커야 합니다 (ZeroDivision 방지).")
        self.min_score = min_score
        self.max_score = max_score

    ## 5. _validate_and_extract() — 한 행을 검사하고 점수 반환
    def _validate_and_extract(self, row: dict) -> float:  # 이름 앞의 언더바 하나 _는 클래스 내부에서 사용할 메서드라는 관례
        if "score" not in row or row["score"] is None:  # ① score가 없거나 None이면 오류를 발생
            raise DataValidationError("score 키가 없거나 None입니다.") 
        
        try:
            val = float(row["score"])  # ② 숫자로 변환
        except (ValueError, TypeError) as exc:
            raise DataValidationError(f"숫자로 변환할 수 없는 값('{row['score']}')입니다.") from exc
            # from exc는 “새로 발생시킨 오류의 원인은 원래 오류 exc다”라고 연결하는 예외 체이닝
            # -> 예를 들어 "N/A"를 숫자로 바꾸다 발생한 ValueError를 원인으로 남기면서, 바깥에는 DataValidationError로 전달함
        
        if not (self.min_score <= val <= self.max_score): # ③ 허용 범위를 확인
            raise DataValidationError(f"허용 범위({self.min_score}~{self.max_score}) 초과: {val}")
        return val # 모든 검사를 통과하면 val을 반환

    def transform(self, dataset: list[dict]) -> PreprocessReport:
        normalized = []
        skipped = []
        span = self.max_score - self.min_score

        ## 6. transform() — 전체 데이터 처리
        # -> 검증에 실패하면 제외 사유를 기록하고, 성공하면 다음 공식으로 정규화
        for idx, row in enumerate(dataset, start=1):
            try:
                raw_val = self._validate_and_extract(row) 
                print(f'{idx}. raw_val: {raw_val}')
            except DataValidationError as err:
                skipped.append(f"Row {idx}: {err}")
                print(f'{idx}. skipped: {skipped}')
            else:
                norm_val = round((raw_val - self.min_score) / span, 4) # (점수 - 최솟값) ÷ (최댓값 - 최솟값)
                normalized.append(norm_val)
                print(f'{idx}. normalized: {normalized}')
            print('---')
        return PreprocessReport(normalized_scores=normalized, skipped_rows=skipped) # 마지막에는 두 리스트를 담은 보고서 객체를 반환

raw_dataset = [
    {"id": 1, "score": "85.0"},
    {"id": 2, "score": "N/A"},      # 변환 오류 -> 안전 격리
    {"id": 3, "score": 120},        # 범위 초과 -> 안전 격리
    {"id": 4, "score": 92.5},
    {"id": 5},                      # 키 누락 -> 안전 격리
]

processor = SafeScorePreprocessor(0.0, 100.0)
report = processor.transform(raw_dataset)

print("정규화 결과:", report.normalized_scores)  # 정규화 결과: [0.85, 0.925]
print("제외된 행 로그:", report.skipped_rows)  # 제외된 행 로그: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다.", 'Row 3: 허용 범위(0.0~100.0) 초과: 120.0', 'Row 5: score 키가 없거나 None입니다.']
print(f"전처리 성공률: {report.success_rate}%")  # 전처리 성공률: 40.0%


## 실행 결과:
# 1. raw_val: 85.0
# 1. normalized: [0.85]
# 2. skipped: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다."]
# 3. skipped: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다.", 'Row 3: 허용 범위(0.0~100.0) 초과: 120.0']
# 4. raw_val: 92.5
# 4. normalized: [0.85, 0.925]
# 5. skipped: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다.", 'Row 3: 허용 범위(0.0~100.0) 초과: 120.0', 'Row 5: score 키가 없거나 None입니다.']
# 정규화 결과: [0.85, 0.925]
# 제외된 행 로그: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다.", 'Row 3: 허용 범위(0.0~100.0) 초과: 120.0', 'Row 5: score 키가 없거나 None입니다.']
# 전처리 성공률: 40.0%
# (py313) imijeong@imijeong-ui-MacBookPro day3 % python day3-3-3.py
# 1. raw_val: 85.0
# 1. normalized: [0.85]
# ---
# 2. skipped: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다."]
# ---
# 3. skipped: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다.", 'Row 3: 허용 범위(0.0~100.0) 초과: 120.0']
# ---
# 4. raw_val: 92.5
# 4. normalized: [0.85, 0.925]
# ---
# 5. skipped: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다.", 'Row 3: 허용 범위(0.0~100.0) 초과: 120.0', 'Row 5: score 키가 없거나 None입니다.']
# ---
# 정규화 결과: [0.85, 0.925]
# 제외된 행 로그: ["Row 2: 숫자로 변환할 수 없는 값('N/A')입니다.", 'Row 3: 허용 범위(0.0~100.0) 초과: 120.0', 'Row 5: score 키가 없거나 None입니다.']
# 전처리 성공률: 40.0%