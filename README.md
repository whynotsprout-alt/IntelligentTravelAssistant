# IntelligentTravelAssistant

基于 HelloAgents + FastAPI + Vue3 的智能旅行规划项目，支持多智能体行程生成、地图展示、景点图片补全、预算估算与导出。

## 前提条件

- Python 3.10+
- Node.js 16+
- 高德地图 API Key（Web 服务 API + JS API）
- LLM API Key（兼容 OpenAI 协议的服务商）

## 技术栈

### 后端

- Agent 框架：HelloAgents（`SimpleAgent` 风格）
- API：FastAPI
- MCP 工具：`amap-mcp-server`（景点/天气/酒店检索）
- 高德 HTTP 服务封装：POI、天气、地理编码、路线、静态地图
- LLM：兼容 OpenAI 协议（通过 `.env` 配置模型、地址、密钥）

### 前端

- 框架：Vue 3 + TypeScript
- 构建工具：Vite
- UI 组件库：Ant Design Vue
- 地图服务：高德地图 JavaScript API（`@amap/amap-jsapi-loader`）
- HTTP 客户端：Axios
- 导出：`html2canvas` + `jsPDF`

## 主要功能

- 多智能体协同生成旅行计划（景点、天气、酒店、规划）
- 行程结果地图可视化（点位 + 路线）
- 景点图片自动检索（Unsplash）
- 行程编辑与预算明细展示
- 导出 PNG / PDF（含地图与景点图）

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

## 运行方式

配置说明（密钥获取与填写）：

- 见 `docs/CONFIGURATION.md`

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
python run.py
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

## 关键接口

- `POST /api/v1/trip/plan`：生成旅行计划
- `GET /api/v1/poi/photo`：获取景点图片
- `POST /api/v1/map/static-map-image`：生成导出用地图图片（data URL）
- `GET /api/v1/health`：服务健康检查
