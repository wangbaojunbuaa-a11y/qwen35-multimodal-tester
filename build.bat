@echo off
echo 正在打包 Qwen3.5 多模态测试工具...
pip install pyinstaller -q
pyinstaller --onefile --windowed --name Qwen35MultimodalTester --icon=icon.ico qwen35_multimodal_tester.py 2>nul
if %errorlevel% neq 0 (
    pyinstaller --onefile --windowed --name Qwen35MultimodalTester qwen35_multimodal_tester.py
)
echo.
echo 打包完成! 可执行文件位于: dist\Qwen35MultimodalTester.exe
pause