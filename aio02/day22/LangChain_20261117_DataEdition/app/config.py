from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

ROOT = Path(__file__).resolve().parents[1]
# load_dotenv(".env", override=False)
load_dotenv(find_dotenv(), override=False)

@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    max_output: int = 500
    temperature: float | None = None

    @classmethod
    def read(cls, mock=False):
        provider = "mock" if mock else os.getenv("LLM_PROVIDER", "openai").lower()
        
        if provider not in {"openai", "groq", "mock"}:
            raise ValueError("LLM_PROVIDER는 openai/groq/mock 중 하나여야 합니다.")
        prefix = provider.upper()
        model = "local-fixture" if provider == "mock" else os.getenv(prefix + "_MODEL", "").strip()
        
        if not model:
            raise ValueError(prefix + "_MODEL에 계정에서 허용된 모델 ID를 설정하세요.")
        if provider != "mock" and not os.getenv(prefix + "_API_KEY", "").strip():
            raise ValueError(prefix + "_API_KEY가 없습니다. .env를 확인하세요.")
        
        raw = os.getenv("LLM_TEMPERATURE", "").strip()
        temperature = float(raw) if raw else None
        if temperature is not None and not 0 <= temperature <= 2:
            raise ValueError("LLM_TEMPERATURE는 0~2 범위여야 합니다.")
        return cls(provider, model, temperature=temperature)
