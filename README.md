# 汉字谜盒

汉字谜盒是一款用聊天方式玩的中文猜字谜游戏。DeepSeek 负责出题、判断答案和给出提示。每局游戏的对话保存在本地，刷新页面后可以打开记录继续猜。

## 玩法

- 在输入框发送「出一道字谜」，收到谜面后直接输入你猜的汉字。
- 卡住时可以发送「提示一下」「公布答案」或「换一题」。
- 在左侧新建游戏、打开历史会话或删除记录。右上角可以切换浅色和深色主题。

## 本地运行

准备 Python 3.10 或更新版本，并申请一个 DeepSeek API 密钥。 [DeepSeek 接入说明](https://api-docs.deepseek.com/zh-cn/)

克隆仓库后，在包含 `main.py` 的仓库根目录打开 PowerShell，执行以下命令。把 `你的 DeepSeek API Key` 替换成自己的密钥。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn openai
$env:DEEPSEEK_API_KEY = '你的 DeepSeek API Key'
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

启动后，打开 [游戏页面](http://127.0.0.1:8000/) 或 [交互式 API 文档](http://127.0.0.1:8000/docs)。`DEEPSEEK_API_KEY` 只需在启动服务的终端中设置，提交项目时请排除真实密钥和 `sessions/` 中的对话记录。

## 项目结构

```text
.
├── main.py           # FastAPI 接口、DeepSeek 调用与会话存储
├── static/
│   ├── index.html    # 游戏页面
│   ├── style.css     # 布局与主题
│   └── app.js        # 聊天交互与会话管理
└── sessions/         # 启动时自动创建，按会话保存 JSON 文件
```

前端使用 HTML、CSS 和原生 JavaScript。FastAPI 提供页面和接口，通过 OpenAI Python SDK 调用 DeepSeek 的 `deepseek-flash` 模型。每次发送消息时，后端读取对应会话的历史，将历史和本次输入一起交给模型，再保存这一轮问答。 [DeepSeek 接入说明](https://api-docs.deepseek.com/zh-cn/)

## API 一览

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/sessions` | 创建会话并返回会话 ID |
| `GET` | `/api/sessions` | 获取会话列表 |
| `GET` | `/api/sessions/{session_id}` | 读取指定会话的历史 |
| `DELETE` | `/api/sessions/{session_id}` | 删除指定会话 |
| `POST` | `/api/chat` | 接收 `session_id` 和 `message`，返回模型回复 |
