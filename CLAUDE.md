# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

青年财务助手 — Flask 驱动的个人预算与分析系统。单文件后端 + 单页面前端，JSON 文件持久化。

## 常用命令

```bash
# 激活虚拟环境并启动开发服务器
cd FlaskWebProject1 && env/Scripts/python.exe app.py
# 运行在 http://localhost:5000，debug 模式开启

# 安装依赖
cd FlaskWebProject1 && env/Scripts/pip install -r requirements.txt
```

Python 3.9，Windows 环境。无测试框架，无 lint 配置。

## 架构

**后端** (`FlaskWebProject1/app.py`)：单个 Flask 实例，6 个 REST API 端点，全部返回 `{success: bool, ...}` 格式。

- `GET /` — 返回 `templates/index.html`
- `POST /api/transactions` — 添加交易（必填字段：type, amount, category, date）
- `GET /api/transactions` — 列出全部交易
- `DELETE /api/transactions/<int:tx_id>` — 按 ID 删除
- `GET /api/dashboard` — 仪表板聚合数据（本月收支、分类统计、预算进度、智能建议、最近10条记录）
- `PUT /api/budget` — 更新月度预算

**数据层**：`finance_data.json` 存储全部数据，结构为 `{transactions: [], monthly_budget: 3000}`。交易记录含 id（时间戳+hash生成）、type、amount、category、date、note、created_at。

**前端** (`templates/index.html`)：纯 HTML/CSS/JS 单页面，Chart.js 渲染饼图。30 秒自动轮询刷新。无模块化、无打包。

**关键约定**：
- 月度过滤基于 `date` 字段，兼容 YYYY-MM-DD、ISO 格式、Unix 时间戳
- 交易 ID 为整数，`DELETE /api/transactions/<int:tx_id>` 使用 Flask int 转换器
- 预算默认值 3000，存储在 JSON 中而非硬编码
