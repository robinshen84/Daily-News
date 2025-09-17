#!/usr/bin/env python3
"""
日报自动生成器 - 启动器
制作者：靠谱瓦叔
"""

import os
import sys
import time
import threading
import webbrowser
from datetime import datetime

def show_startup_info():
    """显示启动信息"""
    print("=" * 60)
    print("📰 日报自动生成器")
    print("=" * 60)
    print(f"🎨 制作者: 靠谱瓦叔")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version.split()[0]}")
    print("=" * 60)
    print()
    print("🚀 正在启动应用...")
    print("⏳ 请稍候...")
    print()

def auto_open_browser():
    """3秒后自动打开浏览器"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 已自动打开浏览器")
    except:
        print("❌ 无法自动打开浏览器，请手动访问: http://localhost:5000")

def main():
    """主函数"""
    show_startup_info()
    
    try:
        # 启动浏览器打开线程
        browser_thread = threading.Thread(target=auto_open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 导入并启动Flask应用
        from app import app
        
        print("✅ 应用启动成功!")
        print("📖 访问地址: http://localhost:5000")
        print("🛑 按 Ctrl+C 停止服务")
        print("-" * 60)
        
        # 启动Flask应用（生产模式，不显示调试信息）
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n")
        print("👋 感谢使用日报自动生成器！")
        print("🎨 制作者：靠谱瓦叔")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n🔧 请检查以下事项:")
        print("1. 确保所有依赖已安装: pip install -r requirements.txt")
        print("2. 确保端口5000未被占用")
        print("3. 确保Python版本为3.7+")
        input("\n按任意键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()
