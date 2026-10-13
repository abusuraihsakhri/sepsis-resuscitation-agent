"""Local deterministic adapter. No remote LLM provider is implemented."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Sepsis Resuscitation Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} local mock]: No model inference or clinical "
            f"verification performed. Query received for demonstration: '{prompt[:60]}...'."
        )


class LLMFactory:
    @staticmethod
    def create(provider: str = "mock", system_name: str = "Sepsis Resuscitation Agent"):
        if str(provider).lower() in {"mock", "deterministic", "test"}:
            return MockLLM(system_name)
        raise ValueError(
            f"Unsupported provider: {provider}. Only the local mock adapter is implemented."
        )
