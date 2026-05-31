"""
AI 客户端统一接口
支持：
  - 线上：OpenAI / DeepSeek / 任意 OpenAI 兼容接口
  - 线下：Ollama（本地部署模型，如 qwen2.5、llama3）
"""
import json
import httpx
from openai import AsyncOpenAI
from app.config import settings


class AIClient:
    """
    统一的 AI 调用客户端。
    根据 settings.AI_BACKEND 自动路由到对应后端。
    """

    def __init__(self):
        self.backend = settings.AI_BACKEND

        # 初始化 OpenAI 兼容客户端（用于 openai / deepseek）
        if self.backend in ("openai", "deepseek"):
            self._openai = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

    async def chat(self, system_prompt: str, user_content: str) -> str:
        """
        发送 chat 请求，返回模型的文本回复。

        Args:
            system_prompt: 系统提示词
            user_content:  用户输入内容

        Returns:
            模型输出的字符串
        """
        if self.backend in ("openai", "deepseek"):
            return await self._chat_openai(system_prompt, user_content)
        elif self.backend == "ollama":
            return await self._chat_ollama(system_prompt, user_content)
        else:
            raise ValueError(f"不支持的 AI_BACKEND: {self.backend}")

    # ------------------------------------------------------------------ #
    # 线上：OpenAI / DeepSeek
    # ------------------------------------------------------------------ #
    async def _chat_openai(self, system_prompt: str, user_content: str) -> str:
        response = await self._openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_content},
            ],
            temperature=0.1,   # 低温度，输出更稳定
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------ #
    # 线下：Ollama
    # ------------------------------------------------------------------ #
    async def _chat_ollama(self, system_prompt: str, user_content: str) -> str:
        """
        调用本地 Ollama HTTP API。
        Ollama 支持 OpenAI 兼容接口（/v1/chat/completions），直接复用。
        """
        ollama_openai = AsyncOpenAI(
            api_key="ollama",   # Ollama 不校验 key，随便填
            base_url=f"{settings.OLLAMA_BASE_URL}/v1",
        )
        response = await ollama_openai.chat.completions.create(
            model=settings.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_content},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()

    async def ping(self) -> str:
        """
        连通性探测：让模型回复一个简单的 'OK'。
        用于 /health 接口内部验证。
        """
        reply = await self.chat(
            system_prompt="你是一个助手，只需要回复 'OK'，不要说其他任何内容。",
            user_content="请回复 OK",
        )
        return reply


# 单例，全局复用
ai_client = AIClient()
