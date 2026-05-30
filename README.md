# 青年财务助手

基于 Flask 的个人财务管理与预算分析系统。(本人的第一个小项目，不喜勿喷谢谢！)

## 快速开始

```bash
cd FlaskWebProject1
pip install -r requirements.txt
python app.py
# 访问 http://localhost:5000
```

## 功能

- 收支记录管理
- 月度预算设定与三色预警
- Chart.js 消费分类饼图
- 5 层智能分析建议引擎
- PWA 支持（手机浏览器安装）

## 技术栈

Python 3.9 / Flask / Chart.js / JSON

## 手机端使用

同 WiFi 下手机浏览器访问 `http://电脑IP:5000`，添加到主屏幕即可像 App 一样使用。

## 常见问题

### 启动报错 `ModuleNotFoundError: No module named 'flask_cors'`
依赖未安装：`pip install -r requirements.txt`

### 电脑没装 Python
去 [python.org](https://python.org) 下载安装（3.9 以上版本），安装时勾选 **Add Python to PATH**

### macOS 端口 5000 被占用
Mac 的 AirPlay 默认占用 5000 端口，两种解决方式：
- 系统设置 → 通用 → AirDrop 与 Handoff → 关闭 AirPlay 接收器
- 或修改 `app.py` 最后一行的 `port=5000` 为 `port=5001`

### 手机连不上
1. 确认手机和电脑连同一个 WiFi
2. 确认 Flask 已启动（终端有 `Running on http://0.0.0.0:5000`）
3. Windows 防火墙弹窗选"允许访问"
4. 确认访问的是电脑 IP 而非 localhost（终端输入 `ipconfig` 查看 IP）

### 前端图表不显示
Chart.js 和 Font Awesome 走 CDN 加载，需要联网。
