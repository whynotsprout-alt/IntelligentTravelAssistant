# helloagents-trip-planner

智能旅行助手项目骨架，已同步如下技术要求。

## 前提条件

- Python 3.10+
- Node.js 16+
- 高德地图 API Key（Web 服务 API + JS API）
- LLM API Key（OpenAI / DeepSeek 等兼容提供商）

## 技术栈

### 后端

- Agent 框架：HelloAgents（`SimpleAgent` 风格）
- API：FastAPI
- MCP 工具：`amap-mcp-server`（当前为服务层占位，后续可接入）
- LLM：多提供商配置（OpenAI / DeepSeek / 兼容接口）

### 前端

- 框架：Vue 3 + TypeScript
- 构建工具：Vite
- UI 组件库：Ant Design Vue
- 地图服务：高德地图 JavaScript API（`@amap/amap-jsapi-loader`）
- HTTP 客户端：Axios

## Project Structure

```text
helloagents-trip-planner/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── trip_planner_agent.py
│   │   ├── api/
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── trip.py
│   │   │       └── map.py
│   │   ├── services/
│   │   │   ├── amap_service.py
│   │   │   └── llm_service.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── config.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── views/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Run

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

配置环境变量：

```bash
cp .env.example .env
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

配置环境变量：

```bash
cp .env.example .env
```
