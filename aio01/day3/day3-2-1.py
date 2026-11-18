names = ['홍길동', '이순신', '강감찬']

id = 1
for name in names : 
    id += 1
    print(f'{id}.{name}')
print('------')

# for id, name in enumerate(names, start=1) :
for id, name in enumerate(names) :
    print(f'{id}.{name}')
print('------------------------------------------------------------')


# 2. 실습 예제 5-1 & 5-2: 깨진 로그 라인을 격리하고 완주하는 무중단 AI 학습 로그 파서
## -> 이 코드는 학습 로그를 한 줄씩 읽고, 정상 데이터만 딕셔너리로 모으는 함수
raw_logs = [
    "epoch=1,loss=0.45,acc=88.5",
    "epoch=2,loss=invalid,acc=91.0",   # ValueError 발생 라인 ('invalid'는 float 변환 불가)
    "epoch=3,loss=0.31",               # KeyError 발생 라인 ('acc' 키 누락)
    "epoch=4,loss=0.22,acc=94.2",
]

def parse_training_logs(logs: list[str]) -> list[dict]:
    
    valid_records = []

    for idx, line in enumerate(logs, start=1):
        try:
            parts = dict(item.split("=") for item in line.split(","))
            print(f'parts: {parts}')
            record = {
                "epoch": int(parts["epoch"]),
                "loss": float(parts["loss"]),
                "acc": float(parts["acc"]),
            }
            print(f'record: {record}')
        except ValueError as e: # as e : 발생한 예외 객체를 e라는 이름으로 받아 오류 내용을 출력할 수 있게 함
            print(f"[Line {idx} 변환 오류] 숫자 형식이 아닙니다: '{line}' ({e})")

        except KeyError as e:
            print(f"[Line {idx} 필드 누락] 필수 키 {e} 가 없습니다: '{line}'")

        else:
            valid_records.append(record)
            print(f'valid_records: {valid_records}')
            print(f"[Line {idx} 정상 수집] Epoch {record['epoch']} -> Accuracy: {record['acc']}%")

        finally:
            pass  # 각 라인 검사 완료 후 스트림 상태 점검 위치
        print('---')

    print(f"[파서 종료] 총 {len(logs)}건 중 {len(valid_records)}건 정상 로드 완료.")
    return valid_records

parsed = parse_training_logs(raw_logs)
## 실행 결과 
# ------------------------------------------------------------
# parts: {'epoch': '1', 'loss': '0.45', 'acc': '88.5'}
# record: {'epoch': 1, 'loss': 0.45, 'acc': 88.5}
# record: {'epoch': 1, 'loss': 0.45, 'acc': 88.5}
# [Line 1 정상 수집] Epoch 1 -> Accuracy: 88.5%
# ---
# parts: {'epoch': '2', 'loss': 'invalid', 'acc': '91.0'}
# [Line 2 변환 오류] 숫자 형식이 아닙니다: 'epoch=2,loss=invalid,acc=91.0' (could not convert string to float: 'invalid')
# ---
# parts: {'epoch': '3', 'loss': '0.31'}
# [Line 3 필드 누락] 필수 키 'acc' 가 없습니다: 'epoch=3,loss=0.31'
# ---
# parts: {'epoch': '4', 'loss': '0.22', 'acc': '94.2'}
# record: {'epoch': 4, 'loss': 0.22, 'acc': 94.2}
# record: {'epoch': 4, 'loss': 0.22, 'acc': 94.2}
# [Line 4 정상 수집] Epoch 4 -> Accuracy: 94.2%
# ---
# [파서 종료] 총 4건 중 2건 정상 로드 완료.
# ---
# ['epoch=1,loss=0.45,acc=88.5', 'epoch=2,loss=invalid,acc=91.0', 'epoch=3,loss=0.31', 'epoch=4,loss=0.22,acc=94.2']

# 4. 예외처리로 잘못된 줄만 제외하기
# 구문	                 역할
# try	                로그 분리와 숫자 변환 시도
# except ValueError	    숫자로 변환할 수 없는 값 등의 오류 처리
# except KeyError	    필요한 키가 없을 때 처리
# else	                try가 성공했을 때만 정상 기록 추가
# finally	            해당 반복의 정리 작업 위치
print('---')
print(raw_logs)
# ['epoch=1, loss=0.45, acc=88.5', 'epoch=2, loss=invalid, acc=91.0', 'epoch=3, loss=0.31', 'epoch=4, loss=0.22, acc=94.2']
