import os 
from dotenv import load_dotenv, find_dotenv
from pinecone import Pinecone 
from langchain_openai import OpenAIEmbeddings 

load_dotenv(find_dotenv(), override=True)

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
embeddings = OpenAIEmbeddings(model=os.getenv('OPENAI_EMBEDDING_MODEL'))

query = '버터 마늘 새우랑 어울리는 와인'
query_vec = embeddings.embed_query(query)

res = index.query(
    vector=query_vec,
    top_k=3,
    include_metadata=True,
    namespace=os.getenv('PINECONE_NAMESPACE')
)

for match in res['matches'] :
    meta = match.get('metadata') or {}
    print(f'점수: {match['score']:.4f} 내용: {meta.get('text', '')}')
