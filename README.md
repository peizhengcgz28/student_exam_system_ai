# 题目提取微服务

基于 FastAPI 的题目智能提取服务，支持线上（OpenAI/DeepSeek）和线下（Ollama）AI。

## 项目结构

```
question-extractor/
├── .env                        # 环境变量配置
├── .env.example                # 环境变量示例
├── requirements.txt            # 依赖
├── app/
│   ├── main.py                 # FastAPI 入口，端口 8001
│   ├── config.py               # 配置加载
│   ├── services/
│   │   ├── ai_client.py        # AI 客户端（线上/线下统一接口）
│   │   └── extractor.py        # 题目提取核心函数
│   └── routers/
│       ├── health.py           # GET /health
│       └── extract.py          # POST /extract
└── tests/
    ├── test_health.py
    └── test_extractor.py
```

## 快速启动

```bash
pip install -r requirements.txt
cp .env.example .env        # 填写你的 API Key
uvicorn app.main:app --port 8001 --reload
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | /health | 健康检查 + AI 连通性验证 |
| POST | /extract | 提交试卷文本，返回题目 JSON |

## 支持的 AI 后端

- **线上**：OpenAI (gpt-4o), DeepSeek, 任意 OpenAI 兼容接口
- **线下**：Ollama (qwen2.5, llama3, 等本地模型)
