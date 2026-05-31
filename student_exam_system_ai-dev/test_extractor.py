from app.services.extractor import extract_questions

test_paper = """
1. 以下哪个是Python的Web框架？（单选题）
A. Django B. Spring C. Vue
答案：A
解析：Django是Python专用Web框架

2. Python是编译型语言。（判断题）
答案：错误
解析：Python是解释型语言
"""

if __name__ == "__main__":
    questions = extract_questions(test_paper)
    print("提取完成，共", len(questions), "道题")