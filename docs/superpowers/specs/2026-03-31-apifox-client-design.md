# apifox-client Skill 设计文档

**日期：** 2026-03-31  
**状态：** 已审阅

---

## 概述

`apifox-client` 是对现有 `apifox` skill 的增强版，提供两类能力：

1. **fetch**：从 Apifox API 读取一个或多个接口定义，供模型根据用户提示词生成请求代码（如 axios、OpenFeign）
2. **sync**：将本项目接口推送到 Apifox（沿用现有 apifox skill 的 sync 逻辑）

---

## 配置文件

路径：`.claude/apifox-client/config.json`（应加入 `.gitignore`）

```json
{
  "accessToken": "AK-your-token-here",
  "projects": [
    {
      "name": "backend",
      "projectId": 123456,
      "capabilities": ["read", "sync"],
      "moduleId": 78901,
      "folderId": null,
      "overwriteBehavior": "OVERWRITE_EXISTING",
      "openApiUrl": ""
    }
  ]
}
```

### 字段说明

| 字段 | 说明 | 必填条件 |
|------|------|----------|
| `accessToken` | Apifox API 访问令牌 | 必填 |
| `name` | 项目标签，命令中用于指定目标 | 必填 |
| `projectId` | Apifox 项目 ID | 必填（`"read"` 或 `"sync"` 均需要） |
| `capabilities` | 支持的操作：`"read"`、`"sync"` | 必填 |
| `moduleId` | 模块 ID | `"sync"` 时必填 |
| `folderId` | 文件夹 ID，null = 根目录 | 可选 |
| `overwriteBehavior` | `OVERWRITE_EXISTING` \| `AUTO_MERGE` \| `KEEP_EXISTING` \| `CREATE_NEW` | sync 时可选，默认 `OVERWRITE_EXISTING` |
| `openApiUrl` | 运行中服务的 OpenAPI spec URL，sync 时优先使用 | 可选 |

### 校验规则（init 时检查）

- `capabilities` 含 `"sync"` → `moduleId` 必填
- `capabilities` 含 `"read"` → `projectId` 必填

---

## 子命令

### `init`

```
/apifox-client init
```

1. 检测项目根目录（有 `.git` 的最近祖先，或当前目录）
2. 若 `.claude/apifox-client/config.json` 已存在，告知用户并跳过
3. 写入配置模板
4. 将 `.claude/apifox-client/config.json` 加入 `.gitignore`

---

### `fetch`

```
/apifox-client fetch <project> <id或名称> [id或名称...]
```

**示例：**
```
/apifox-client fetch backend 123456
/apifox-client fetch backend 123456 789012
/apifox-client fetch backend "用户登录"
/apifox-client fetch backend 123456 "获取订单列表"
```

**执行流程：**

1. 读取配置，校验项目存在且 `capabilities` 含 `"read"`
2. 对每个参数判断类型：
   - 纯数字 → `GET /v1/projects/{projectId}/http-apis/{id}` 精确获取
   - 字符串 → `GET /v1/projects/{projectId}/http-apis?keywords={name}` 搜索
     - 命中多条时列出结果，让用户确认选哪个
3. 将所有接口定义整理输出
4. 输出后提示用户告知需要生成什么代码

**输出格式：**
```
[接口 1] POST /api/users/login
  描述：用户登录
  请求体：{ username: string, password: string }
  响应：{ token: string, userId: number }

[接口 2] GET /api/orders/{id}
  描述：获取订单详情
  路径参数：id (integer)
  响应：{ id: number, status: string, items: array }
```

**使用 Apifox API：**
- 按 ID：`GET https://api.apifox.com/v1/projects/{projectId}/http-apis/{apiId}`
- 搜索：`GET https://api.apifox.com/v1/projects/{projectId}/http-apis?keywords={name}`
- 请求头：`Authorization: Bearer {accessToken}`、`X-Apifox-Api-Version: 2024-03-28`

---

### `sync`

```
/apifox-client sync [project] [接口范围]
```

**示例：**
```
/apifox-client sync
/apifox-client sync admin
/apifox-client sync backend /users /orders
/apifox-client sync backend UserController
```

逻辑与现有 `apifox` skill 的 sync 完全一致，唯一差异：
- 校验项目 `capabilities` 含 `"sync"`，否则报错提示

**执行步骤（沿用 apifox skill）：**
1. 读取配置，解析 target 和接口范围
2. 获取 OpenAPI spec（优先 `openApiUrl`，否则扫描源码）
3. 上传到 `POST https://api.apifox.com/v1/projects/{projectId}/import-openapi`
4. 展示结果（created/updated/failed 统计）
5. 删除临时文件

---

## Guardrails

- Token 输出时显示为 `AK-****`，不打印完整值
- 多个项目且未指定时，必须询问用户选择哪个
- fetch 搜索命中多条时，列出候选让用户确认
- sync 成功后立即删除临时文件
- capabilities 不符合时，明确报错并提示原因
