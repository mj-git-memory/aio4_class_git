from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from app.catalog import find_product, product_context
from app.prompts import get_prompt


def prepare_input(request, records):
    if not isinstance(request, dict):
        raise TypeError("요청은 dict여야 합니다.")
    question = request.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question은 공백이 아닌 문자열이어야 합니다.")
    question = question.strip()
    if len(question) > 500:
        raise ValueError("질문은 500자 이내로 입력하세요.")
    record_id = request.get("record_id")
    if not isinstance(record_id, str):
        raise ValueError("record_id가 필요합니다.")
    product = find_product(records, record_id)
    # 고객이 넘긴 context는 사용하지 않고 카탈로그에서 직접 구성한다.
    return {"context": product_context(product), "question": question}


def build_chain(model, records, version="designed"):
    prepare = RunnableLambda(lambda request: prepare_input(request, records))
    return prepare | get_prompt(version) | model | StrOutputParser()


def sample_requests(records):
    indices = [0, 2, 8] if len(records) >= 9 else list(range(min(3, len(records))))
    questions = ["15인치 노트북을 넣을 수 있나요? 반품이 가능한가요?",
                 "어떤 활동에 적합한 상품인가요? 현재 재고가 있나요?",
                 "지원하는 운영체제는 무엇인가요? 배송일은 언제인가요?"]
    return [{"record_id": records[j]["record_id"], "question": questions[i]} for i, j in enumerate(indices)]
