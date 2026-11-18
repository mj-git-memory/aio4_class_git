# pip install openai
from openai import OpenAI

# 1. LM Studio 로컬 서버 연결
client = OpenAI(
    base_url="http://localhost:1235/v1",
    api_key="lm-studio"
)

# 2. 사용 가능한 모델 확인
mds = client.models.list()

if not mds.data:
    raise RuntimeError("사용 가능한 모델이 없습니다.")

# model_id = mds.data[0].id
model_id = "qwen/qwen3.5-9b"
print(f"사용 모델: {model_id}")

# # 3. 대화 기록 초기화
# messages = [
#     {
#         "role": "system",
#         "content": "너는 친절하고 이해하기 쉽게 답변하는 한국어 AI 어시스턴트야."
#     }
# ]

# print("\n=== 로컬 AI 챗봇 ===")
# print("대화를 종료하려면 '종료' 또는 'exit'를 입력하세요.\n")

# # 4. 채팅 반복 실행
# while True:
#     user_input = input("나: ").strip()

#     # 빈 입력은 무시
#     if not user_input:
#         continue

#     # 종료 명령
#     if user_input.lower() in ["종료", "exit", "quit"]:
#         print("챗봇: 대화를 종료합니다.")
#         break

#     # 사용자 메시지 저장
#     messages.append({
#         "role": "user",
#         "content": user_input
#     })

#     try:
#         # 5. 모델에 대화 요청
#         response = client.chat.completions.create(
#             model="qwen/qwen3.5-9b",
#             messages=[
#                 {"role": "user", "content": "안녕! 자기소개를 해줘."}
#             ],
#             temperature=0.7,
#             max_tokens=200)

#         # 6. AI 답변 추출
#         assistant_reply = response.choices[0].message.content

#         if assistant_reply is None:
#             assistant_reply = "답변을 생성하지 못했습니다."

#         print(f"\n챗봇: {assistant_reply}\n")

#         # AI 답변도 대화 기록에 저장
#         messages.append({
#             "role": "assistant",
#             "content": assistant_reply
#         })

#     except Exception as e:
#         print(f"\n오류 발생: {e}\n")
#         # 실패한 사용자 메시지는 대화 기록에서 제거
#         messages.pop()
