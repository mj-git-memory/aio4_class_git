"""쇼핑몰 상품 상세 페이지로 배우는 동기/비동기 실험.

프로젝트 루트에서 실행:
    python -m uvicorn day7.shop_lab:app --port 8010
단일 worker를 사용해야 blocking 모드의 이벤트 루프 지연을 관찰할 수 있다.
"""

import asyncio
import time
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="장바구니 밖의 Python · 동기/비동기 실험실")
# WEB = Path(__file__).with_name("shop-web")
WEB = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=WEB), name="static")

Mode = Literal["sync", "await", "gather", "tasks", "blocking", "thread"]
Service = Literal["stock", "delivery", "reviews"]
SERVICES = {
    "stock": {"label": "재고 확인", "delay": 0.6, "value": "구매 가능 · 재고 12개"},
    "delivery": {"label": "배송 조회", "delay": 0.9, "value": "무료배송 · 주문 후 2일 내 출고"},
    "reviews": {"label": "리뷰 조회", "delay": 1.2, "value": "★ 4.9 · 리뷰 128개"},
}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/health")
async def health():
    """대기 없는 요청. 이벤트 루프가 막히면 이 요청도 기다린다."""
    return {"status": "ok"}


def legacy_lookup(delay: float):
    """비동기를 지원하지 않는 기존 I/O 라이브러리의 대기를 흉내 낸다."""
    time.sleep(delay)


@app.get("/api/service/{service}")
async def service_api(
    service: Service,
    behavior: Literal["async", "blocking", "thread"] = "async",
    scale: float = Query(1, ge=0.5, le=2),
):
    info = SERVICES[service]
    started = time.perf_counter()
    delay = info["delay"] * scale
    if behavior == "blocking":
        # 의도적인 잘못된 예: 현재 이벤트 루프 스레드를 멈춘다.
        legacy_lookup(delay)
    elif behavior == "thread":
        # 기존 동기 I/O 함수를 작업 스레드에 맡기고 결과를 기다린다.
        await asyncio.to_thread(legacy_lookup, delay)
    else:
        # 실제 외부 API/DB를 기다리는 상황을 재현한다.
        await asyncio.sleep(delay)
    return {"service": service, **info, "started": started, "ended": time.perf_counter()}


def sync_requests(base_url: str, scale: float):
    """일반 def + httpx.Client: 요청 하나가 끝나야 다음 요청을 보낸다."""
    results = []
    with httpx.Client(base_url=base_url, timeout=20, trust_env=False) as client:
        for service in SERVICES:
            response = client.get(f"/api/service/{service}", params={"scale": scale})
            response.raise_for_status()
            results.append(response.json())
    return results


@app.get("/api/run")
async def run(request: Request, mode: Mode = "gather", scale: float = Query(1, ge=0.5, le=2)):
    # 같은 서버의 모의 API에 실제 HTTP 요청을 보낸다. 외부 네트워크는 필요 없다.
    # 사용자 입력 Host로 외부 요청을 보내지 않고 로컬 포트만 사용한다.
    base_url = f"http://127.0.0.1:{request.url.port or 80}"
    started = time.perf_counter()
    if mode == "sync":
        # 실험용 동기 클라이언트가 서버 전체를 멈추지 않도록 밖에서 스레드에 맡긴다.
        # sync_requests 내부의 세 요청 자체는 동기·순차 실행이다.
        results = await asyncio.to_thread(sync_requests, base_url, scale)
    else:
        behavior = {"blocking": "blocking", "thread": "thread"}.get(mode, "async")
        async with httpx.AsyncClient(base_url=base_url, timeout=20, trust_env=False) as client:

            async def fetch(service):
                response = await client.get(
                    f"/api/service/{service}", params={"behavior": behavior, "scale": scale}
                )
                response.raise_for_status()
                return response.json()

            if mode == "await":
                results = []
                for service in SERVICES:
                    results.append(await fetch(service))
            elif mode == "tasks":
                # 먼저 모두 등록한다. create_task 직후마다 await하면 순차 실행이 된다.
                tasks = [asyncio.create_task(fetch(service)) for service in SERVICES]
                results = [await task for task in tasks]
            else:
                results = await asyncio.gather(*(fetch(service) for service in SERVICES))

    elapsed = time.perf_counter() - started
    for result in results:
        result["start"] = round(result.pop("started") - started, 4)
        result["end"] = round(result.pop("ended") - started, 4)
    return {"mode": mode, "elapsed": elapsed, "results": results, "scale": scale}
