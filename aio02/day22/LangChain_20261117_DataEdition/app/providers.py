from app.config import Settings

MOCK_TEXT = "[모의 응답] 안녕하세요. 상품 설명과 질문을 연결하는 형식을 확인했습니다. 재고·배송·반품 정책은 별도 확인이 필요합니다. 문의별 실제 답변을 생성한 결과는 아닙니다."

def make_model(settings: Settings):
    if settings.provider == "mock":
        from langchain_core.language_models.fake_chat_models import FakeListChatModel
        return FakeListChatModel(responses=[MOCK_TEXT])
    common = dict(model=settings.model, max_tokens=settings.max_output,
                  timeout=30, max_retries=0)
    # temperature를 지원하지 않는 모델을 위해 미설정 시 전달하지 않는다.
    if settings.temperature is not None:
        common["temperature"] = settings.temperature
    if settings.provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(**common)
    if settings.provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(**common)
    raise ValueError("지원하지 않는 공급자입니다.")

def friendly_error(error):
    status = getattr(error, "status_code", None)
    if status in {400, 401, 403, 404, 429}:
        return {400: "요청 설정 오류: 모델과 파라미터 지원을 확인하세요.",
                401: "인증 오류: API 키를 확인하세요.",
                403: "권한 오류: 프로젝트와 모델 권한을 확인하세요.",
                404: "모델/주소 오류: 사용 가능한 모델 ID를 확인하세요.",
                429: "호출/토큰/크레딧 한도: 콘솔 확인 후 기다렸다가 수동 재실행하세요."}[status]
    if isinstance(error, (ValueError, KeyError, TypeError, FileNotFoundError)):
        return str(error)
    # 외부 오류 본문·헤더·키를 그대로 로그에 기록하지 않는다.
    return f"{type(error).__name__}: 연결/타임아웃/공급자 상태를 확인하세요."
