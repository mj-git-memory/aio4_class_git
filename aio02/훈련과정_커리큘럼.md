# 단일 에이전트 추론 및 AI 오케스트레이션

| 날짜 | 대주제 | 세부 주제 | 학습 내용 | 실습 내용 |
|---|---|---|---|---|
| 2026-11-17 | 단일 에이전트 추론 및 AI 오케스트레이션 | 고급 프롬프트 및 추론 전략 | LangChain ChatPromptTemplate 프롬프트 템플릿·LCEL 체인 기초 소개, 역할(Role)·지시문(Instruction)·맥락(Context) 기반 프롬프트 설계, 응답 품질 비교 및 분석 | [Python] LangChain 프레임워크 설치, ChatPromptTemplate 적용 및 체인(LCEL) 로직 설계 실습 |
| 2026-11-18 | 단일 에이전트 추론 및 AI 오케스트레이션 | 고급 프롬프트 및 추론 전략 | CoT·ReAct 기반 단계적 문제 해결 프롬프트 설계, 추론 품질 비교 | CoT(Chain of Thought) 및 ReAct 프롬프트 작성, [생성형 AI API]의 단계적 추론 과정 관찰 |
| 2026-11-19 | 단일 에이전트 추론 및 AI 오케스트레이션 | 고급 프롬프트 및 추론 전략 | LangChain with_structured_output(Pydantic) 활용, JSON Schema 기반 Structured Output 구현, 안정적인 데이터 응답 제어 | Structured Output 제어 기법을 적용, JSON Schema로 [생성형 AI API] 응답 포맷팅 강제화 실습 |
| 2026-11-20 | 단일 에이전트 추론 및 AI 오케스트레이션 | 고급 프롬프트 및 추론 전략 | Prompt Injection 이해 및 입력 검증, 시스템 프롬프트 기반 보안 적용 | Prompt Injection 방어 프롬프트 작성, [LangSmith]를 연동하여 입력/추론 이력 대시보드 모니터링 |
| 2026-11-23 | 단일 에이전트 추론 및 AI 오케스트레이션 | Function Calling 및 오케스트레이션 | LLM 외부 기능 호출(Function Calling) 구조 이해 및 활용 | [생성형 AI API]의 Function Calling JSON 스키마 작성 및 파라미터 추출(Tool Use) 동작 원리 파악 |
| 2026-11-24 | 단일 에이전트 추론 및 AI 오케스트레이션 | Function Calling 및 오케스트레이션 | LangChain Tool 바인딩 활용, 외부 API 및 Python 함수 Tool 등록, LLM 연동 | [Python] 함수를 @tool 데코레이터로 감싸 LLM에 바인딩, 동적 함수 호출 테스트 |
| 2026-11-25 | 단일 에이전트 추론 및 AI 오케스트레이션 | Function Calling 및 오케스트레이션 | MCP 기반 외부 도구 연결 구조 실습, Function Calling과 MCP 활용 방식 비교 | MCP(Model Context Protocol) 개념 실습, [Postman]을 활용한 외부 API 호출 테스트와 LLM Tool 연동 비교 |
| 2026-11-26 | 단일 에이전트 추론 및 AI 오케스트레이션 | Function Calling 및 오케스트레이션 | 검색·계산·데이터 조회 Tool 활용, Multi-Tool Agent 구현 | 검색 도구와 외부 API 연동 도구를 결합한 [Python] 기반 Multi-Tool 단일 에이전트 구축 실습 |
| 2026-11-27 | 단일 에이전트 추론 및 AI 오케스트레이션 | Function Calling 및 오케스트레이션 | 다중 Tool 결과 통합, Agent 의사결정 Workflow 구현 | 사용자 입력 조건 분기에 따라 알맞은 Tool을 라우팅(Routing)하는 체인 파이프라인 통합 구현 |
| 2026-11-30 | 단일 에이전트 추론 및 AI 오케스트레이션 | 지식 저장소 및 장기 기억 | 임베딩 개념, 임베딩(Embedding) 기반 텍스트 벡터화, 임베딩 시각화, Vector DB 저장·검색 구조 학습 | 텍스트 임베딩(Embedding) 원리 학습, [Python] 기반 로컬 벡터 검색(FAISS 등)을 통한 유사도 측정 |
| 2026-12-01 | 단일 에이전트 추론 및 AI 오케스트레이션 | 지식 저장소 및 장기 기억 | PostgreSQL 기반 Session Memory 구성, 사용자별 대화 상태 및 단기 기억 관리 | [PostgreSQL] 연동, 세션 메모리(Session Memory) 관리를 위한 DB 기반 대화 상태 및 이력 적재 실습 |
| 2026-12-02 | 단일 에이전트 추론 및 AI 오케스트레이션 | 지식 저장소 및 장기 기억 | PostgreSQL + pgvector 기반 장기 기억 저장, RAG(검색 증강 생성) 개념, 검색(RAG) 구조 구현, 문서 파싱·청킹 전략이 검색 품질에 미치는 영향 | [PostgreSQL] (pgvector 활성화) 벡터 DB 구축, 문서 청킹 및 장기 기억(Long-term) RAG 저장 실습 |
| 2026-12-03 | 단일 에이전트 추론 및 AI 오케스트레이션 | 지식 저장소 및 장기 기억 | 키워드 검색·벡터 검색 결합, 하이브리드 검색 및 검색 기반 응답 생성, RRF(Reciprocal Rank Fusion) 점수 융합, 리랭킹(Re-ranking), RAG 품질 평가(RAGAS) | 키워드 + 벡터(pgvector) 기반 하이브리드 검색 구현, RAG 품질 평가 프레임워크(RAGAS) 적용 |
| 2026-12-04 | 단일 에이전트 추론 및 AI 오케스트레이션 | 상태 기계 기반 흐름 제어 | LangGraph Node·Edge·State 구조 활용, Agent 상태 전이 흐름 구현 | [LangGraph] StateGraph를 이용한 에이전트의 노드(Node), 엣지(Edge), 상태(State) 설계 및 구성 실습 |
| 2026-12-07 | 단일 에이전트 추론 및 AI 오케스트레이션 | 상태 기계 기반 흐름 제어 | PostgreSQL(Session)·Vector DB(Long-term) 결합, Hybrid Memory 구조 구현 | Session 메모리와 Vector DB 결합 구조를 [LangGraph] 체크포인터(Checkpointer) 로직에 통합 구현 |
| 2026-12-08 | 단일 에이전트 추론 및 AI 오케스트레이션 | 상태 기계 기반 흐름 제어 | Agent 자기 평가(Self-Reflection), 응답 품질 개선 및 반복 실행 구조 구현 | LLM-as-a-Judge 기법 적용: 에이전트가 응답을 자기 평가(Self-Reflection)하고 재시도하는 순환 그래프 작성 |
| 2026-12-09 | 단일 에이전트 추론 및 AI 오케스트레이션 | 상태 기계 기반 흐름 제어 | Agent 실행 추적(Tracing), 계획(Planning)·디버깅 및 성능 평가 | [LangSmith] 연동, 복잡한 에이전트 실행 추적(Trace)을 통한 디버깅 및 프롬프트 최적화 |