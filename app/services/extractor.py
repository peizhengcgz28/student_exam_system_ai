"""
题目提取核心模块

支持题型：
  - choice        单选题
  - multi_choice  多选题
  - judge         判断题
  - short_answer  简答题
"""
import json
import re
from typing import List, Dict, Any

from app.services.ai_client import ai_client


# ------------------------------------------------------------------ #
# Prompt 模板
# ------------------------------------------------------------------ #
EXTRACT_SYSTEM_PROMPT = """你是一个专业的题目解析器。
从用户提供的试卷文本中，提取所有题目，以 JSON 数组格式输出。

每个题目对象的字段定义如下：
- type         : 题型，只能是以下之一：
                   choice（单选题）
                   multi_choice（多选题）
                   judge（判断题）
                   short_answer（简答题）
- stem         : 题干文本（字符串）
- options      : 选项数组（单选/多选题填写，如 ["A. 选项1","B. 选项2"]；判断题和简答题填 []）
- answer       : 答案（字符串，多选题用逗号分隔字母，如 "A,C"）
- analysis     : 解析/解题思路（字符串，若无则填 ""）

输出要求：
1. 只输出 JSON 数组，不要有任何前缀、后缀、代码块符号（不要用 ```json）
2. 严格保证 JSON 格式合法，可被 json.loads() 直接解析
3. 如果文本中没有识别到任何题目，返回空数组 []
"""


# ------------------------------------------------------------------ #
# 公开函数
# ------------------------------------------------------------------ #
async def extract_questions(raw_text: str) -> List[Dict[str, Any]]:
    """
    从试卷文本中提取所有题目。

    Args:
        raw_text: 原始试卷文本（可包含多种题型）

    Returns:
        题目列表，每个元素为包含 type/stem/options/answer/analysis 的字典

    Raises:
        ValueError: 模型返回内容无法解析为合法 JSON
    """
    if not raw_text or not raw_text.strip():
        return []

    # 调用 AI
    raw_output = await ai_client.chat(
        system_prompt=EXTRACT_SYSTEM_PROMPT,
        user_content=raw_text,
    )

    # 解析 JSON（模型偶尔会多出 ```json ... ``` 包裹，做容错处理）
    questions = _parse_json_output(raw_output)

    # 字段校验与补全
    return [_normalize_question(q) for q in questions]


# ------------------------------------------------------------------ #
# 内部工具函数
# ------------------------------------------------------------------ #
def _parse_json_output(text: str) -> List[Dict]:
    """容错解析：去除可能的 markdown 代码块包裹后解析 JSON"""
    text = text.strip()

    # 去除 ```json ... ``` 或 ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"模型输出无法解析为 JSON: {e}\n原始输出:\n{text}")

    if not isinstance(result, list):
        raise ValueError(f"期望 JSON 数组，实际得到: {type(result)}")

    return result


VALID_TYPES = {"choice", "multi_choice", "judge", "short_answer"}

def _normalize_question(q: Dict) -> Dict[str, Any]:
    """确保每个题目对象包含所有必要字段，并做基本类型修正"""
    return {
        "type":     q.get("type", "short_answer") if q.get("type") in VALID_TYPES else "short_answer",
        "stem":     str(q.get("stem", "")).strip(),
        "options":  q.get("options", []) if isinstance(q.get("options"), list) else [],
        "answer":   str(q.get("answer", "")).strip(),
        "analysis": str(q.get("analysis", "")).strip(),
    }
