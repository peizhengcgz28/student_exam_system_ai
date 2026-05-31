"""
题目提取核心函数单元测试
使用 mock 模拟 AI 返回，不依赖真实 API Key
"""
import json
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.services.extractor import extract_questions, _parse_json_output, _normalize_question
from app.main import app


# ------------------------------------------------------------------ #
# 模拟试卷文本（涵盖四种题型）
# ------------------------------------------------------------------ #
MOCK_EXAM_TEXT = """
2024年计算机基础期末试卷

一、单选题（每题2分）
1. 下列哪个协议工作在网络层？
A. HTTP  B. TCP  C. IP  D. FTP
答案：C
解析：IP 协议工作在 OSI 模型的网络层。

二、多选题（每题4分）
2. 以下属于关系型数据库的是？
A. MySQL  B. Redis  C. PostgreSQL  D. MongoDB
答案：A, C
解析：MySQL 和 PostgreSQL 是关系型数据库，Redis 是键值存储，MongoDB 是文档数据库。

三、判断题（每题1分）
3. Python 是一种编译型语言。（ ）
答案：错误
解析：Python 是解释型语言。

四、简答题（每题10分）
4. 简述 TCP 三次握手的过程。
答案：SYN → SYN-ACK → ACK
解析：第一次握手客户端发送 SYN；第二次服务端回复 SYN-ACK；第三次客户端发送 ACK。
"""


# 对应 mock_exam_text 的预期 AI 输出
MOCK_AI_RESPONSE = json.dumps([
    {
        "type": "choice",
        "stem": "下列哪个协议工作在网络层？",
        "options": ["A. HTTP", "B. TCP", "C. IP", "D. FTP"],
        "answer": "C",
        "analysis": "IP 协议工作在 OSI 模型的网络层。"
    },
    {
        "type": "multi_choice",
        "stem": "以下属于关系型数据库的是？",
        "options": ["A. MySQL", "B. Redis", "C. PostgreSQL", "D. MongoDB"],
        "answer": "A,C",
        "analysis": "MySQL 和 PostgreSQL 是关系型数据库。"
    },
    {
        "type": "judge",
        "stem": "Python 是一种编译型语言。",
        "options": [],
        "answer": "错误",
        "analysis": "Python 是解释型语言。"
    },
    {
        "type": "short_answer",
        "stem": "简述 TCP 三次握手的过程。",
        "options": [],
        "answer": "SYN → SYN-ACK → ACK",
        "analysis": "第一次握手客户端发送 SYN；第二次服务端回复 SYN-ACK；第三次客户端发送 ACK。"
    }
], ensure_ascii=False)


# ------------------------------------------------------------------ #
# 单元测试：extract_questions 核心函数
# ------------------------------------------------------------------ #
@pytest.mark.asyncio
async def test_extract_questions_returns_four_items():
    """正常试卷文本应解析出 4 道题"""
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MOCK_AI_RESPONSE
        questions = await extract_questions(MOCK_EXAM_TEXT)

    assert len(questions) == 4


@pytest.mark.asyncio
async def test_extract_question_types():
    """四道题的题型应正确识别"""
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MOCK_AI_RESPONSE
        questions = await extract_questions(MOCK_EXAM_TEXT)

    types = [q["type"] for q in questions]
    assert types == ["choice", "multi_choice", "judge", "short_answer"]


@pytest.mark.asyncio
async def test_extract_choice_question_has_options():
    """单选题应包含 4 个选项"""
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MOCK_AI_RESPONSE
        questions = await extract_questions(MOCK_EXAM_TEXT)

    choice_q = questions[0]
    assert choice_q["type"] == "choice"
    assert len(choice_q["options"]) == 4
    assert choice_q["answer"] == "C"


@pytest.mark.asyncio
async def test_extract_judge_question_no_options():
    """判断题的 options 应为空列表"""
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MOCK_AI_RESPONSE
        questions = await extract_questions(MOCK_EXAM_TEXT)

    judge_q = questions[2]
    assert judge_q["type"] == "judge"
    assert judge_q["options"] == []


@pytest.mark.asyncio
async def test_extract_empty_text_returns_empty():
    """空文本应直接返回空列表，不调用 AI"""
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        result = await extract_questions("   ")
        mock_chat.assert_not_called()

    assert result == []


@pytest.mark.asyncio
async def test_extract_invalid_json_raises_value_error():
    """AI 返回非法 JSON 时应抛出 ValueError"""
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "这不是 JSON"
        with pytest.raises(ValueError, match="无法解析为 JSON"):
            await extract_questions("some text")


@pytest.mark.asyncio
async def test_extract_markdown_wrapped_json():
    """AI 返回 ```json...``` 包裹时也能正确解析"""
    wrapped = f"```json\n{MOCK_AI_RESPONSE}\n```"
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = wrapped
        questions = await extract_questions(MOCK_EXAM_TEXT)

    assert len(questions) == 4


# ------------------------------------------------------------------ #
# 单元测试：_normalize_question 字段补全
# ------------------------------------------------------------------ #
def test_normalize_fills_missing_fields():
    """缺失字段应被补全为默认值"""
    q = _normalize_question({"stem": "什么是 HTTP?"})
    assert q["type"] == "short_answer"
    assert q["options"] == []
    assert q["answer"] == ""
    assert q["analysis"] == ""


def test_normalize_invalid_type_defaults_to_short_answer():
    """无效的 type 应被修正为 short_answer"""
    q = _normalize_question({"type": "essay", "stem": "写一篇作文"})
    assert q["type"] == "short_answer"


# ------------------------------------------------------------------ #
# 集成测试：POST /extract 接口
# ------------------------------------------------------------------ #
@pytest.mark.asyncio
async def test_api_extract_endpoint():
    """POST /extract 接口应返回 200 和正确的题目数量"""
    with patch("app.services.extractor.ai_client.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MOCK_AI_RESPONSE
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/extract", json={"text": MOCK_EXAM_TEXT})

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 4
    assert len(data["questions"]) == 4


@pytest.mark.asyncio
async def test_api_extract_empty_text_returns_422():
    """POST /extract 传入空字符串应返回 422"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/extract", json={"text": ""})

    assert resp.status_code == 422
