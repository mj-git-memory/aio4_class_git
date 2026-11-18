"""실행 중인 단일-worker 서버의 실제 HTTP 동작 확인.

python day7/shop-web/check.py [http://127.0.0.1:8010]
"""

import asyncio
import sys
import time

import httpx


async def check(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=30, trust_env=False) as client:
        for path in ("/", "/static/app.js", "/static/style.css", "/docs"):
            response = await client.get(path)
            response.raise_for_status()
        measurements = {}
        for mode in ("sync", "await", "gather", "tasks", "blocking", "thread"):
            response = await client.get("/api/run", params={"mode": mode, "scale": 0.5})
            response.raise_for_status()
            data = response.json()
            measurements[mode] = data["elapsed"]
            results = data["results"]
            assert [item["service"] for item in results] == ["stock", "delivery", "reviews"]
            assert all(0 <= item["start"] < item["end"] <= data["elapsed"] + 0.01 for item in results)
            if mode in ("sync", "await", "blocking"):
                ordered = sorted(results, key=lambda item: item["start"])
                assert all(a["end"] <= b["start"] for a, b in zip(ordered, ordered[1:])), mode
            else:
                assert max(item["start"] for item in results) < min(item["end"] for item in results), mode
            print(f"{mode:10} {data['elapsed']:.3f}s · 처리 순서 확인")

        # 단순 절대 시간 대신 실제 측정된 순차/동시 시간의 관계를 확인한다.
        assert measurements["gather"] < measurements["await"]
        assert measurements["thread"] < measurements["blocking"]

        health_times = {}
        for mode in ("gather", "blocking", "thread"):
            pending = asyncio.create_task(client.get("/api/run", params={"mode": mode, "scale": 1}))
            await asyncio.sleep(0.2)
            started = time.perf_counter()
            health = await client.get("/api/health")
            health.raise_for_status()
            health_times[mode] = time.perf_counter() - started
            (await pending).raise_for_status()
            print(f"{mode:10} /health {health_times[mode]:.3f}s")
        assert health_times["blocking"] > 0.5, "단일 worker 서버에서 실행하세요"
        assert health_times["blocking"] > health_times["gather"]
        assert health_times["blocking"] > health_times["thread"]

        for params in ({"mode": "unknown"}, {"scale": 0}, {"scale": 3}):
            response = await client.get("/api/run", params=params)
            assert response.status_code == 422
        print("PASS · 정적 화면, 6개 모드, 이벤트 루프 지연, 입력 검증")


if __name__ == "__main__":
    asyncio.run(check(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8010"))
