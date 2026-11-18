from fastapi import FastAPI

app = FastAPI(title="인사 API", version="1.0.0")


# @app.get("/greet", summary="이름으로 인사", include_in_schema=False) # -> 에러 발생
@app.get("/greet", summary="이름으로 인사", include_in_schema=True) # -> 수정 시 에러 안남 
def greet(name: str = "guest"):
    return {"message": f"Hello, {name}!"}
