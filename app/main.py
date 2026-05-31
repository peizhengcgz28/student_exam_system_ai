"""
题目提取微服务入口
监听端口：8001
"""
from fastapi import FastAPI
from app.routers import health, extract

app = FastAPI(
    title="题目提取微服务",
    description="智能提取试卷题目，支持线上（OpenAI/DeepSeek）和线下（Ollama）AI",
    version="1.0.0",
)

# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(extract.router, tags=["题目提取"])


@app.get("/")
async def root():
    return {
        "service": "题目提取微服务",
        "docs": "/docs",
        "health": "/health",
        "extract": "POST /extract",
    }


# 直接运行时使用（开发调试）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
