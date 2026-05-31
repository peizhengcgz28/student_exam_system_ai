# 学生作答系统 - AI 微服务

- 独立的 AI 能力服务，提供题目结构化提取、纸质试卷电子化、智能组卷等工作流，通过 REST API 供后端调用。

## 技术栈 (参考)

- Python 3.10+
- FastAPI
- OpenAI / DeepSeek / Qwen-VL 等大模型 API
- pdfplumber / python-docx / Pillow / OpenCV
- PaddleOCR (可选)
- pydantic-settings

## 项目结构 (参考)

```
ai-service/
├── app/
│ ├── api/
│ │ └── v1/
│ │ ├── health.py # 健康检查
│ │ └── workflows.py # 工作流接口
│ ├── core/
│ │ └── config.py # 配置与环境变量
│ ├── services/
│ │ ├── extractor.py # 题目提取核心逻辑
│ │ ├── ocr.py # OCR 与图像预处理
│ │ └── llm_client.py # 大模型调用封装
│ └── main.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```


## 环境准备

1. **安装依赖**
   
```bash
pip install -r requirements.txt
```

2. 环境变量

> .env 并修改配置：

```ini
OPENAI_API_KEY=sk-xxx          # 若使用 OpenAI
DEEPSEEK_API_KEY=sk-xxx        # 若使用 DeepSeek
MODEL_NAME=gpt-4o              # 默认模型
MAX_FILE_SIZE_MB=10
```

3. 启动服务

```bash
uvicorn app.main:app --reload --port 8001
```

## API 文档

- 启动后访问 http://localhost:8001/docs 查看 Swagger 交互文档。



## 题目获取模块 (test)

- 获取题目后，输出json格式案例；

```json
[
  {
    "type": "choice",
    "stem": "下列哪个选项是Python的注释符号？",
    "options": ["//", "/*", "#", "<!--"],
    "answer": "C",
    "analysis": "Python中使用#表示单行注释。"
  },
  {
    "type": "short_answer",
    "stem": "请简述Python中列表和元组的区别。",
    "options": [],
    "answer": "列表是可变的，元组是不可变的。",
    "analysis": "列表支持增删改，元组一旦创建不可修改。"
  },
  {
    "type": "choice",
    "stem": "Python中输出\"Hello World\"的正确函数是？",
    "options": ["print(\"Hello World\")", "echo(\"Hello World\")", "console.log(\"Hello World\")", "System.out.println(\"Hello World\")"],
    "answer": "A",
    "analysis": "Python中使用print()函数进行输出。"
  }
]
```