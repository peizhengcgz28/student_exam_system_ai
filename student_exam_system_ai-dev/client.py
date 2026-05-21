# client.py
# 专门用来调用你自己的接口，独立运行
import requests

# 1. 测试健康检查接口 (GET)
def test_health():
    BASE_URL = "http://localhost:8001"
    response = requests.get(f"{BASE_URL}/health")
    print("=== 健康检查结果 ===")
    print("状态码：", response.status_code)
    print("返回结果：", response.json())

# 2. 测试题目提取接口 (POST)
def test_extract():
    BASE_URL = "http://localhost:8001"
    
    test_text = """
1. 以下哪个是Python的Web框架？（单选题）
A. Django
B. Spring
C. Vue
答案：A
解析：Django是Python的Web框架
    """
    
    data = {"content": test_text}
    response = requests.post(
        url=f"{BASE_URL}/extract-questions",
        json=data
    )
    
    print("\n=== 题目提取结果 ===")
    print("状态码：", response.status_code)
    print("提取的题目：", response.json())

# 直接运行测试
if __name__ == "__main__":
    test_health()
    test_extract()