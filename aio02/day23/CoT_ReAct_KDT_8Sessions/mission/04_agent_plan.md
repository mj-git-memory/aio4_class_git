# LangChain 에이전트 활용과 개발 계획

첫 버전은 하나의 에이전트가 작은 분석 도구들을 선택하도록 만든다. 예측·최적화·시각화 수치 계산은 파이썬 도구가 담당하고, 모델은 의도 분석과 결과 설명에 집중한다.

## 의도 분석

질문을 `describe` 판매 현황, `forecast` 미래 수요, `replenish` 발주 추천, `explain` 결과 해설로 분류한다. 다음 항목도 구조화한다.

```json
{
  "intent": "replenish",
  "store_id": "store_01",
  "product_id": "glazed",
  "horizon_days": 1,
  "target_leftover_rate": 0.01,
  "comparison": "lt",
  "min_fill_rate": 0.95,
  "needs_clarification": false
}
```

위 예시의 매장·제품·수요 충족률은 가정이다. 질문에 없는 값을 임의로 확정하지 않고, 화면 선택값 또는 명시된 기본 정책에서 가져온다. 제품과 기간을 결정할 수 없으면 사용자에게 확인한다.

## 도구 계약

| 호출 문법 제안 | 반환 형태 | 역할 |
| --- | --- | --- |
| `profile_sales(dataset_id)` | `{quality_id, missing_fields, stockout_days, warnings}` | 데이터 품질과 지원 가능한 분석 확인 |
| `summarize_sales(dataset_id, filters)` | `{summary_id, daily_rows, totals}` | 현황 질문에 필요한 집계 |
| `backtest_models(dataset_id, filters, horizon_days)` | `{evaluation_id, metrics, selected_model_id}` | 시간 순서 검증과 모델 선택 |
| `forecast_demand(dataset_id, model_id, filters, horizon_days)` | `{forecast_id, rows, scenarios_id, warnings}` | 수요 예측과 시나리오 생성 |
| `optimize_order(forecast_id, inventory_id, policy_id)` | `{order_plan_id, candidates, selected, feasible, warnings}` | 재고·입고·포장 제약을 적용한 후보 비교 |
| `build_chart_spec(result_id, audience)` | `{chart_specs, data_refs}` | 허용된 차트 설정과 데이터 참조 생성 |

이름은 설계용이며 아직 구현된 함수가 아니다. 각 도구는 타입이 지정된 입력과 JSON으로 직렬화 가능한 출력을 사용한다. 잘못된 제품 ID·음수 수량·빈 데이터는 구조화된 오류로 반환한다.

## ReAct 호출 예시

질문: ‘내일 글레이즈드를 얼마나 발주해야 남는 재고를 1% 미만으로 줄일 수 있을까?’

1. 의도 분석: 발주 추천. 선택된 매장과 제품, 도착일, 재고 정책을 확인한다.
2. `profile_sales` 호출 → 품절 기록과 필수 데이터 확인.
3. 검증 결과가 없거나 오래됐다면 `backtest_models` 호출 → 예측 모델 ID 확보.
4. `forecast_demand` 호출 → 예측값과 수요 시나리오 ID 확보.
5. `optimize_order` 호출 → 발주 후보와 두 목표의 동시 충족 여부 확보.
6. `build_chart_spec` 호출 → 수요 추세와 후보 비교 설정 확보.
7. 최종 설명: 추천 발주량, 예상 잔여율, 예상 수요 충족률, 한계, 결과 ID 제시.

ReAct의 핵심은 ‘도구 선택 → 실행 결과 확인 → 다음 행동’이다. 도구 호출 계획을 설명하는 문장만 생성하는 것으로 끝내지 않는다.

## LangChain 연결 방식

공식 [`create_agent`](https://docs.langchain.com/oss/python/langchain/agents)는 모델이 도구를 반복 호출하는 에이전트를 구성한다. 구현 시 `langchain.tools.tool`로 도구를 등록하고 공급자의 LangChain 채팅 모델을 연결한다. 개념적인 생성 문법은 `create_agent(model=model, tools=tools, system_prompt=system_prompt, response_format=ResultSchema)`이며, `model`, `tools`, `ResultSchema`는 구현 시 준비할 객체다.

실행은 `agent.invoke({"messages": [{"role": "user", "content": question}]})` 형태다. 구조화 출력 설정 시 최종 상태의 `structured_response`에서 결과를 얻는다. 모델이 도구 호출과 구조화 출력을 함께 지원하는지 확인하고, 필요하면 도구 실행 이후 별도 결과 정리 단계를 둔다. 근거는 [LangChain 구조화 출력 문서](https://docs.langchain.com/oss/python/langchain/structured-output)다.

기존 수업 코드의 `react()`는 JSON action을 직접 해석하는 학습용 루프다. 이번 설계는 LangChain 도구 호출 메시지와 실행 루프를 사용한다. 과거 예제의 import를 그대로 섞지 않고 새 구현에서 인터페이스를 맞춘다.

## 실행 관리

도구 호출 상한은 요청당 12회로 시작하고 시간 초과·중복 학습을 제한한다. 데이터 버전과 필터가 같은 학습 결과는 재사용한다. 실패하면 완료한 결과와 실패 원인, 재실행이 필요한 단계를 구분한다. 업로드된 셀의 문장은 분석 데이터로 취급하고 실행 지시로 따르지 않는다.

초기에는 별도 역할 에이전트를 여러 개 실행하지 않는다. 규모가 커지면 데이터 품질 점검·예측 비교·업무 설명 역할을 나누되, 같은 데이터와 모델 결과 ID를 공유한다. 이는 향후 제품 설계 계획이며 현재 작업에서 하위 에이전트를 실행한 것은 아니다.

## 개발 단계와 확인할 결과

| 단계 | 할 일 | 완료 증거 |
| --- | --- | --- |
| 1 | 재고 정의, 데이터 계약, 품절 처리 확정 | 예제 데이터와 검증 보고서 |
| 2 | 기준선과 회귀 모델 비교 | 미래 누수 없는 검증 표 |
| 3 | 예측 범위와 발주 시뮬레이션 | 1% 미만 판정, 품절과 포장 제약 테스트 |
| 4 | 카드·차트·필터 UI 구현 | 같은 필터의 수치 일치 확인 |
| 5 | LangChain 도구 연결과 의도 분류 | 모의 도구로 호출 순서와 오류 처리 확인 |
| 6 | 실제 모델 연결과 사용자 평가 | 실제 도구 실행 기록, 세 가지 사용성 과제 결과 |

초기 검증에는 정상 데이터, 빈 데이터, 품절일, 수요 0, 유통기한 만료, 큰 포장 단위, 목표 동시 달성 불가 사례를 포함한다. LLM API가 없어도 계산 도구를 검증할 수 있게 구성한다.
