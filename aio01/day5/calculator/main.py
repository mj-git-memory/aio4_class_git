"""두 숫자를 받아 네 가지 연산을 수행하는 FastAPI 앱."""
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="두 숫자 계산기")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class CalculationInput(BaseModel):
    # 문자열로 받은 소수도 Decimal로 검사한다. float의 0.1 + 0.2 오차를 피한다.
    a: Decimal = Field(max_digits=30, decimal_places=10, allow_inf_nan=False)
    b: Decimal = Field(max_digits=30, decimal_places=10, allow_inf_nan=False)


def display(number: Decimal) -> str:
    """불필요한 소수점 뒤 0을 지우고, 음수 0도 0으로 표시한다."""
    if number == 0:
        return "0"
    result = format(number, "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/calculate")
def calculate(payload: CalculationInput):
    # 큰 수의 곱셈도 정확히 계산할 수 있도록 이번 연산의 정밀도를 확보한다.
    with localcontext() as context:
        context.prec = 80
        a, b = payload.a, payload.b
        division = None
        if b != 0:
            # 나눗셈은 소수점 아래 10자리까지 반올림한다.
            division = display((a / b).quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP))
        return {
            "a": display(a),
            "b": display(b),
            "addition": display(a + b),
            "subtraction": display(a - b),
            "multiplication": display(a * b),
            "division": division,
            "division_error": "0으로는 나눌 수 없어요." if b == 0 else None,
        }
