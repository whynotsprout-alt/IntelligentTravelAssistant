# 配置指南（密钥获取与填写）

本文档汇总项目所需配置项：哪些是必须、哪些可选、密钥从哪里获取、以及如何在前后端正确配置。

## 1. 配置总览

### 后端（`backend/.env`）

必填：

- `AMAP_API_KEY`：高德 Web 服务 API Key（后端调用高德 HTTP API）
- `LLM_API_KEY`：大模型服务 API Key（或使用 `OPENAI_API_KEY` 兼容）

强烈建议：

- `UNSPLASH_ACCESS_KEY`：景点图片搜索（不配置会频繁回退占位图）

按需填写（取决于所用模型服务商）：

- `LLM_PROVIDER`：可选；不填时自动识别
- `LLM_BASE_URL`：兼容 OpenAI 协议服务时常需指定
- `LLM_MODEL`：模型名（如 `gpt-5.4`）
- `LLM_TIMEOUT`：模型请求超时（秒），建议 `120`
- `AMAP_JS_API_KEY`：可选，仅用于记录前端 JS Key（后端当前不使用）

### 前端（`frontend/.env`）

必填：

- `VITE_API_BASE_URL`：后端地址（本地通常是 `http://localhost:8000`）
- `VITE_AMAP_WEB_JS_KEY`：高德 JS API Key（Result 页地图加载必需）

## 2. 从哪里获取这些密钥

### 2.1 高德地图 Key（`AMAP_API_KEY` / `VITE_AMAP_WEB_JS_KEY`）

获取入口：<https://lbs.amap.com/>

步骤：

1. 注册/登录高德开放平台。
2. 创建应用。
3. 在应用下分别创建两类 Key：
   - **Web 服务 API** Key -> 用于后端 `AMAP_API_KEY`
   - **Web 端（JS API）** Key -> 用于前端 `VITE_AMAP_WEB_JS_KEY`
4. 给 JS Key 配置允许来源（例如 `http://localhost:5173`）。

### 2.2 LLM Key（`LLM_API_KEY`）

按你使用的平台获取：

- OpenAI：<https://platform.openai.com/>
- 其他兼容平台（DeepSeek、硅基流动、OpenRouter、阿里百炼等）：各自控制台

如果不是 OpenAI 官方接口，通常还要填写：

- `LLM_BASE_URL`
- `LLM_MODEL`

### 2.3 Unsplash Key（`UNSPLASH_ACCESS_KEY`）

获取入口：<https://unsplash.com/developers>

步骤：

1. 登录 Unsplash。
2. 创建开发者应用。
3. 获取 `Access Key` 填入 `UNSPLASH_ACCESS_KEY`。

## 3. 如何配置

### 3.1 后端配置

在 `backend` 目录执行并编辑：

```bash
cp .env.example .env
```

`backend/.env` 示例：

```env
AMAP_API_KEY=你的高德Web服务Key
AMAP_JS_API_KEY=你的高德JSKey(可选)
UNSPLASH_ACCESS_KEY=你的UnsplashAccessKey(建议)
LLM_API_KEY=你的LLM密钥
LLM_PROVIDER=openai
LLM_BASE_URL=https://你的兼容服务/v1
LLM_MODEL=gpt-5.4
LLM_TIMEOUT=120
```

### 3.2 前端配置

在 `frontend` 目录执行并编辑：

```bash
cp .env.example .env
```

`frontend/.env` 示例：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_AMAP_WEB_JS_KEY=你的高德JSKey
```

## 4. 启动前检查清单

- 后端：
  - `AMAP_API_KEY` 已填
  - `LLM_API_KEY`（或 `OPENAI_API_KEY`）已填
- 前端：
  - `VITE_API_BASE_URL` 指向可访问后端
  - `VITE_AMAP_WEB_JS_KEY` 已填
- 导出相关：
  - 后端 `/api/v1/map/static-map-image` 可访问
  - 高德 `AMAP_API_KEY` 有效（导出地图依赖）
- 本地端口：
  - 后端 `8000`
  - 前端 `5173`

## 5. 常见问题

- **地图加载失败**
  - 检查 `VITE_AMAP_WEB_JS_KEY` 是否正确
  - 检查 JS Key 白名单是否包含当前前端地址（如 `http://localhost:5173`）

- **生成行程失败（LLM报错）**
  - 检查 `LLM_API_KEY`
  - 若用兼容平台，补齐 `LLM_BASE_URL` 和 `LLM_MODEL`

- **景点图片总是占位图**
  - 检查 `UNSPLASH_ACCESS_KEY` 是否配置
  - Unsplash 免费额度或搜索命中率可能导致回退

- **接口 404**
  - 前端应请求 `/api/v1/...`
  - `VITE_API_BASE_URL` 应指向后端根地址（不带 `/api`）

- **导出时地图空白 / 仅有标点**
  - 已默认使用后端静态地图图片接口：`/api/v1/map/static-map-image`
  - 先确认后端已重启并加载最新代码
  - 检查 `AMAP_API_KEY` 是否有效、是否有调用额度限制
