"""
配置模块：从 .env 文件加载所有配置项
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # AI 后端选择: openai | deepseek | ollama
    AI_BACKEND: str = os.getenv("AI_BACKEND", "openai")

    # 线上 AI（OpenAI 及兼容接口）
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # 线下 Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    @property
    def active_model(self) -> str:
        """返回当前激活的模型名称（用于展示）"""
        if self.AI_BACKEND == "ollama":
            return self.OLLAMA_MODEL
        return self.OPENAI_MODEL


settings = Settings()
