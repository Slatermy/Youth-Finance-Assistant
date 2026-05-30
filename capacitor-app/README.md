# 青年财务助手 - Android App 构建指南

## 目录结构

```
capacitor-app/
├── capacitor.config.json   # Capacitor 配置（连接 Flask 后端）
├── www/                    # 前端静态文件
│   └── index.html
├── android/                # Android 原生项目（自动生成）
└── node_modules/
```

## 开发模式（实时调试）

```bash
# 1. 先启动 Flask 后端
cd ../FlaskWebProject1
env/Scripts/python.exe app.py

# 2. 另开终端，启动 Android 调试
cd capacitor-app
npx cap run android
# 或手动：Android Studio 打开 android/ 目录，点击 Run
```

## 构建发布 APK

1. 用 Android Studio 打开 `android/` 目录
2. Build → Build Bundle(s) / APK(s) → Build APK(s)
3. APK 输出路径：`android/app/build/outputs/apk/debug/app-debug.apk`

## 部署到真机

1. 将 Flask 后端部署到云服务器（如阿里云 ECS）
2. 修改 `capacitor.config.json` 中的 `server.url` 为服务器地址
3. 重新构建 APK

## 注意事项

- 当前 `server.url` 指向 `http://localhost:5000`，仅用于本地开发
- `cleartext: true` 允许 HTTP 明文传输，生产环境应改为 HTTPS
- 部署到公网前务必关闭 Flask `debug=True` 模式