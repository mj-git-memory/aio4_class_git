import os
import time 
from datasets import load_dataset
from dotenv import load_dotenv, find_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec 

load_dotenv(find_dotenv(), override=True)

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
PINECONE_INDEX_CLOUD = os.getenv('PINECONE_INDEX_CLOUD')
PINECONE_INDEX_REGION = os.getenv('PINECONE_INDEX_REGION')
PINECONE_INDEX_METRIC = os.getenv('PINECONE_INDEX_METRIC')
PINECONE_INDEX_DIMENSION = int(os.getenv('PINECONE_INDEX_DIMENSION'))
PINECONE_NAMESPACE = os.getenv('PINECONE_NAMESPACE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL')

def infer_wine_style(variety: str, description: str) -> str:
    """품종과 리뷰 문구를 바탕으로 검색 필터용 와인 스타일(red/white/sparkling/other)을 분류합니다."""
    text = f"{variety} {description}".lower()
    sparkling_kw = ["champagne", "sparkling", "prosecco", "cava", "brut", "cremant"]
    white_kw = [
        "chardonnay", "sauvignon blanc", "riesling", "pinot grigio", "pinot gris",
        "viognier", "gewurztraminer", "chenin blanc", "semillon", "white blend", "albariño",
    ]
    red_kw = [
        "cabernet", "merlot", "pinot noir", "syrah", "shiraz", "malbec", "zinfandel",
        "sangiovese", "tempranillo", "nebbiolo", "grenache", "red blend", "bordeaux",
    ]
    if any(k in text for k in sparkling_kw):
        return "sparkling"
    if any(k in text for k in white_kw):
        return "white"
    if any(k in text for k in red_kw):
        return "red"
    return "other"


def ensure_pinecone_index() -> Pinecone:
    """Pinecone 인덱스 존재 여부를 확인하고 없으면 Serverless 인덱스를 생성합니다."""
    if not PINECONE_API_KEY:
        raise ValueError(".env 파일에 PINECONE_API_KEY가 설정되어 있지 않습니다.")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing_indexes = {idx["name"] for idx in pc.list_indexes()}

    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"[1/3] Pinecone 인덱스 '{PINECONE_INDEX_NAME}' 생성 중...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=PINECONE_INDEX_DIMENSION,
            metric=PINECONE_INDEX_METRIC,
            spec=ServerlessSpec(
                cloud=PINECONE_INDEX_CLOUD,
                region=PINECONE_INDEX_REGION,
            ),
        )
        while not pc.describe_index(PINECONE_INDEX_NAME).status.get("ready", False):
            time.sleep(1)
        print(f"      인덱스 '{PINECONE_INDEX_NAME}' 생성 완료!")
    else:
        print(f"[1/3] 기존 Pinecone 인덱스 '{PINECONE_INDEX_NAME}' 확인 완료.")

    return pc


def download_and_prepare_documents(limit: int = 150) -> list[Document]:
    """Hugging Face에서 실제 와인 리뷰 데이터를 내려받아 LangChain Document 리스트로 변환합니다."""
    print("[2/3] Hugging Face 'james-burton/wine_reviews' 데이터 다운로드 중...")
    dataset = load_dataset("james-burton/wine_reviews", split="train")
    subset = dataset.select(range(min(limit, len(dataset))))

    documents: list[Document] = []
    for idx, row in enumerate(subset):
        desc = (row.get("description") or "").strip()
        if not desc:
            continue

        variety = str(row.get("variety") or "Unknown").strip()
        country = str(row.get("country") or "Unknown").strip()
        province = str(row.get("province") or "Unknown").strip()
        points = row.get("points")
        price = row.get("price")
        style = infer_wine_style(variety, desc)

        page_content = (
            f"품종(Variety): {variety} | 스타일(Style): {style} | "
            f"원산지(Origin): {country} - {province} | "
            f"평점(Points): {points} | 가격(USD): {price}\n"
            f"테이스팅 리뷰: {desc}"
        )
        metadata = {
            "row_id": idx,
            "variety": variety,
            "style": style,
            "country": country,
            "province": province,
            "points": int(points) if points is not None else -1,
            "price": float(price) if price is not None else -1.0,
        }
        documents.append(Document(page_content=page_content, metadata=metadata))

    print(f"      총 {len(documents)}건의 Document 변환 완료.")
    return documents


def upsert_to_pinecone(documents: list[Document], batch_size: int = 50) -> None:
    """변환된 문서를 OpenAI 임베딩으로 벡터화하여 Pinecone에 배치 적재합니다."""
    print("[3/3] OpenAI 임베딩 생성 및 Pinecone 벡터 업서트 시작...")
    embeddings = OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )
    vector_store = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY,
        namespace=PINECONE_NAMESPACE,
    )

    for start in range(0, len(documents), batch_size):
        batch = documents[start : start + batch_size]
        vector_store.add_documents(batch)
        print(f"      업서트 진행률: {min(start + batch_size, len(documents))} / {len(documents)}")

    print("\n✅ Pinecone 데이터 적재 완료! 이제 step2_wine_pairing_agent.py를 실행할 수 있습니다.")


if __name__ == "__main__":
    ensure_pinecone_index()
    docs = download_and_prepare_documents(limit=150)
    upsert_to_pinecone(docs, batch_size=50)
