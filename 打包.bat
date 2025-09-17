@echo off
chcp 65001 >nul
echo ================================================================
echo 📦 日报生成器 - 带图标打包
echo 🎨 制作者：靠谱瓦叔
echo 🖼️ 图标：6i2n4-yc5gh-001.ico
echo ================================================================
echo.

echo 🔍 检查图标文件...
if not exist "6i2n4-yc5gh-001.ico" (
    echo ❌ 图标文件不存在：6i2n4-yc5gh-001.ico
    pause
    exit /b 1
)
echo ✅ 图标文件存在

echo.
echo 🔍 安装打包依赖...
pip install pyinstaller

echo.
echo 📦 开始打包（带图标）...
pyinstaller --onefile ^
    --add-data "templates;templates" ^
    --icon "6i2n4-yc5gh-001.ico" ^
    --hidden-import flask ^
    --hidden-import werkzeug ^
    --hidden-import jinja2 ^
    --hidden-import PIL ^
    --name "日报生成器_靠谱瓦叔版_带图标" ^
    launcher.py

echo.
if exist "dist\日报生成器_靠谱瓦叔版_带图标.exe" (
    echo ✅ 打包成功！
    echo 📁 文件位置: dist\日报生成器_靠谱瓦叔版_带图标.exe
    echo 🖼️ 图标已应用: 6i2n4-yc5gh-001.ico
) else (
    echo ❌ 打包失败，请检查错误信息
)

echo.
echo 🧹 清理临时文件...
if exist "build" rmdir /s /q "build"
if exist "日报生成器_靠谱瓦叔版_带图标.spec" del "日报生成器_靠谱瓦叔版_带图标.spec"

echo.
echo 🎉 完成！现在你的exe文件有了自定义图标！
pause
