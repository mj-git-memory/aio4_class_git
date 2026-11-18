from langchain_core.prompts import ChatPromptTemplate
from app.catalog import read_catalog, product_context
from app.cli import parser
from app.report import save_report

def main():
    args = parser().parse_args(); records = read_catalog(args.data); product = records[0]
    print(product)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 {role}입니다. 상품 정보: {context}"),
        ("human", "{question}")
    ])
    values = {"role": "상품 안내 도우미", "context": product_context(product),
              "question": "노트북을 넣을 수 있나요? 주문 {order_id}도 조회해 주세요."}
    for m in prompt.invoke(values).to_messages():
        print(m)
        print()
    # print(prompt.invoke({"question": "문의"})) 
    # -> input to ChatPromptTemplate is missing variables {'role', 'context'}.  Expected: ['context', 'question', 'role']

    messages = [{"role": m.type, "content": m.content} for m in prompt.invoke(values).to_messages()]
    try: 
        prompt.invoke({"question": "문의"})
    except KeyError: 
        print("누락 변수 오류 재현: role/context가 필요합니다.")
    print("필수 변수:", sorted(prompt.input_variables))
    save_report(2, records, [{"record_id": product["record_id"], "messages": messages,
                            "status": "prompt_rendered_no_model"}], args.data)

if __name__ == "__main__": main()
