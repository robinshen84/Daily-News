# Daily News Report Generator

🎨 **By: Robin Shen (靠谱瓦叔)**

A full-featured news report generator built with Python Flask. Supports dual-format intelligent parsing (AI news + general news), 42 beautiful color themes, and one-click export to high-quality PNG images.

## ✨ Features

- **🧠 Dual-Format Smart Parsing** — Supports both AI/tech news (numbered list) and general news (title:content) formats
- **🎨 42 Color Themes** — Apple-style, soft nature, business professional, and more
- **📸 One-Click Image Export** — Generate high-quality PNG using Playwright headless browser
- **📱 Mobile-Optimized** — Card-style layout designed for mobile sharing (WeChat, etc.)
- **🎯 Custom Branding** — Upload logo, choose colors, add signatures
- **📦 Standalone Executable** — Package as .exe for Windows distribution
- **🏷️ Smart Tagging** — 16 news category tags with 200+ entity recognition

## 🛠️ Tech Stack

- **Backend:** Python 3.7+ / Flask
- **Frontend:** HTML5 + CSS3 + JavaScript + Bootstrap 5
- **Image Generation:** Playwright (headless browser screenshot)
- **Image Processing:** Pillow

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/robinshen84/Daily-News.git
cd Daily-News

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Launch
python launcher.py
```

The app runs at `http://localhost:5000` and auto-opens your browser.

## 📦 Build Executable

```bash
# Windows - double-click the batch file
打包带图标.bat

# Output in dist/ directory
```

## 📱 News Format Examples

### AI/Tech News Format
```
AI Daily 2025-09-17

1. Alibaba releases FunAudio-ASR model for noise-robust speech recognition.
2. Tencent launches HunYuan3D 3.0 with 36B voxel ultra-HD modeling.
```

### General News Format
```
Trump arrives in UK for state visit: The president landed today accompanied by the First Lady.
Baidu stock surges 7%: Chinese tech giant sees significant gains in US markets.
```

## 📊 Version History

- **v3.0.0** — Dual-format parsing engine, 16 tags, 200+ entity recognition
- **v2.0.0** — 42 color themes (Apple HIG inspired), mobile optimization
- **v1.0.0** — Core functionality, AI news parsing, image export

## 📄 License

MIT License

## 🤝 Contributing

Issues and Pull Requests are welcome!
