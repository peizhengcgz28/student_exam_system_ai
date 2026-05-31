"""
GET /health  —  健康检查 + AI 连通性验证
"""
from fastapi import APIRouter, HTTPException
from app.services.ai_client import ai_client
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    健康检查接口。
    内部会向 AI 发送一次简单请求（让模型回复 OK），
    确认 API Key 有效、网络可达（线上）或 Ollama 在线（线下）。
    """
    try:
        ai_reply = await ai_client.ping()
        ai_ok = "ok" in ai_reply.lower() or "ok" in ai_reply
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "ai_backend": settings.AI_BACKEND,
                "model": settings.active_model,
                "ai_available": False,
                "error": str(e),
            },
        )

    return {
        "status": "ok",
        "ai_backend": settings.AI_BACKEND,   # openai / deepseek / ollama
        "model": settings.active_model,
        "ai_available": True,
        "ai_reply": ai_reply,
    }
