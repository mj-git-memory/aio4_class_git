"""세 공급자에 동일한 Chat Completions 요청을 보낸다."""
import json
import os
import time
from urllib import request, error
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai",
}


class CallLimit(RuntimeError):
    pass


class RemoteChat:
    def __init__(self, provider, max_calls=8, max_tokens=800):
        load_dotenv(find_dotenv(), override=False)
        if provider not in BASE_URLS:
            raise ValueError('provider는 openai/groq/gemini 중 하나입니다.')
        self.provider = provider
        prefix = provider.upper()
        self.key = os.getenv(prefix + '_API_KEY', '').strip()
        self.model = os.getenv(prefix + '_MODEL', '').strip()
        if not self.key or not self.model:
            raise ValueError(f'{prefix}_API_KEY 와 {prefix}_MODEL 설정이 필요합니다.')
        if not 1 <= max_calls <= 30 or not 128 <= max_tokens <= 4096:
            raise ValueError('호출 상한 1~30, 출력 상한 128~4096을 사용하세요.')
        self.max_calls, self.max_tokens = max_calls, max_tokens
        self.calls = 0
        self.metrics = []

    def prepare(self, messages):
        url = BASE_URLS[self.provider] + "/chat/completions"
        headers = {"Authorization": "Bearer " + self.key}
        payload = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": self.max_tokens,
        }
        return url, headers, payload

    def extract(self, data):
        choices = data.get("choices", [])
        if not choices or choices[0].get("finish_reason") != "stop":
            raise ValueError("응답 완료 상태와 출력 한도를 확인하세요.")
        text = choices[0].get("message", {}).get("content")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("응답 본문이 비어 있습니다.")
        return text, data.get("usage", {})

    def __call__(self, messages):
        if self.calls >= self.max_calls:
            raise CallLimit('명령 단위 호출 상한 도달; 자동 공급자 전환 없음')
        self.calls += 1  # 실패 요청도 호출 예산에 포함한다.
        url, headers, payload = self.prepare(messages)
        req = request.Request(url, data=json.dumps(payload).encode('utf-8'),
                              headers={**headers, 'Content-Type': 'application/json'}, method='POST')
        started = time.perf_counter()
        try:
            with request.urlopen(req, timeout=45) as response:
                data = json.load(response)
            text, usage = self.extract(data)
        except error.HTTPError as exc:
            # 응답 본문·요청 헤더를 출력하지 않아 키 노출을 피한다.
            retry = exc.headers.get('Retry-After', '없음')
            raise RuntimeError(f'HTTP {exc.code}; Retry-After={retry}; 설정/한도 확인 후 수동 재실행') from None
        except (error.URLError, TimeoutError):
            raise RuntimeError('연결 실패 또는 45초 타임아웃; 자동 재시도 없음') from None
        self.metrics.append({'seconds': round(time.perf_counter() - started, 3), 'usage': usage})
        return text