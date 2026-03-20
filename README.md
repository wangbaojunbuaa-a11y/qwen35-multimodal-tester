# Qwen3.5-397B 多模态测试工具

一个用于验证 Qwen3.5-397B 模型多模态能力的图形化工具。

## 功能

- ✅ 文本对话测试
- ✅ 图片理解测试
- ✅ 文档解析测试（PDF等）
- ✅ 视频理解测试

## 使用方法

### 方式一：直接运行 EXE（Windows）

1. 下载 `dist/Qwen35MultimodalTester.exe`
2. 双击运行
3. 配置 API 地址和密钥
4. 选择测试类型进行测试

### 方式二：Python 运行

```bash
# 安装依赖
pip install requests

# 运行
python qwen35_multimodal_tester.py
```

## 配置说明

| 配置项 | 说明 |
|--------|------|
| API地址 | 模型服务的 API 端点（如 http://localhost:8000/v1） |
| API密钥 | 如需认证，填写 API Key |
| 模型名称 | 模型标识（如 qwen3.5-397b） |

## 打包方法

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包成单文件
pyinstaller --onefile --windowed --name Qwen35MultimodalTester qwen35_multimodal_tester.py

# 打包后的文件在 dist/ 目录
```

## 支持的文件格式

| 类型 | 格式 |
|------|------|
| 图片 | JPG, JPEG, PNG, GIF, WebP |
| 文档 | PDF |
| 视频 | MP4, WebM, MOV, AVI |

## 截图

![界面预览](screenshot.png)

## License

MIT