from fastapi import FastAPI
from pydantic import BaseModel
import json

# 启动服务
app = FastAPI(title="AI题目提取微服务", version="1.0")

# 测试接口
@app.get("/", summary="服务测试")
def root():
    return {"message": "题目提取服务运行中", "port": 8001}

# ------------------- P0 健康检查（外部调用模式） -------------------
@app.get("/health", summary="健康检查")
def health():
    # 模拟外部AI调用成功
    return {"status": "ok", "model": "gpt-4o"}

# ------------------- P1 对外题目提取API -------------------
class ExtractRequest(BaseModel):
    content: str

@app.post("/extract-questions", summary="提取题目")
def extract_questions_api(req: ExtractRequest):
    # 外部调用AI服务（模拟标准返回结果）
    result = [
        {
            "type": "choice",
            "stem": "测试题干",
            "options": ["A", "B", "C"],
            "answer": "A",
            "analysis": "测试解析"
        }
    ]
    return {"questions": result}