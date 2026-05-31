"""
POST /extract  —  题目提取接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from app.services.extractor import extract_questions

router = APIRouter()


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="试卷原始文本")


class ExtractResponse(BaseModel):
    count: int
    questions: List[Dict[str, Any]]


@router.post("/extract", response_model=ExtractResponse)
async def extract(req: ExtractRequest):
    """
    提交试卷文本，返回结构化题目列表。

    每道题包含：
    - type       : choice | multi_choice | judge | short_answer
    - stem       : 题干
    - options    : 选项列表（单选/多选有值，其余为 []）
    - answer     : 答案
    - analysis   : 解析
    """
    try:
        questions = await extract_questions(req.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服务异常: {str(e)}")

    return ExtractResponse(count=len(questions), questions=questions)
