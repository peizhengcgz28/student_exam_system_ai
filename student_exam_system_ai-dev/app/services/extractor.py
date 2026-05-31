from typing import List

def extract_questions(raw_text: str) -> List[dict]:
    # 模拟外部AI返回的标准格式
    return [
        {
            "type": "choice",
            "stem": "测试题目",
            "options": ["选项1", "选项2"],
            "answer": "选项1",
            "analysis": "测试解析"
        }
    ]