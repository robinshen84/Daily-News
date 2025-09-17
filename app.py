import os
import sys
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import asyncio
from playwright.async_api import async_playwright
import threading
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 预设颜色主题
COLOR_THEMES = {
    # 推荐：护眼舒适配色
    'apple_gray': {
        'name': '🔘 苹果灰（推荐）',
        'primary': '#1C1C1E',
        'secondary': '#8E8E93',
        'accent': '#007AFF',
        'header_gradient': 'linear-gradient(135deg, #F2F2F7 0%, #8E8E93 100%)',
        'footer_gradient': 'linear-gradient(135deg, #8E8E93 0%, #F2F2F7 100%)'
    },
    'soft_mist': {
        'name': '🌫️ 薄雾（推荐）',
        'primary': '#2D3748',
        'secondary': '#718096',
        'accent': '#4FD1C7',
        'header_gradient': 'linear-gradient(135deg, #E6FFFA 0%, #B2F5EA 100%)',
        'footer_gradient': 'linear-gradient(135deg, #B2F5EA 0%, #E6FFFA 100%)'
    },
    'soft_sky': {
        'name': '☁️ 天空蓝（推荐）',
        'primary': '#2D3748',
        'secondary': '#63B3ED',
        'accent': '#4FD1C7',
        'header_gradient': 'linear-gradient(135deg, #E6F6FF 0%, #BEE3F8 100%)',
        'footer_gradient': 'linear-gradient(135deg, #BEE3F8 0%, #E6F6FF 100%)'
    },
    'soft_dawn': {
        'name': '🌅 晨曦（推荐）',
        'primary': '#2D3748',
        'secondary': '#4A5568',
        'accent': '#ED8936',
        'header_gradient': 'linear-gradient(135deg, #FBD38D 0%, #F6AD55 100%)',
        'footer_gradient': 'linear-gradient(135deg, #F6AD55 0%, #FBD38D 100%)'
    },
    
    # 苹果风格配色
    'apple_blue': {
        'name': '🔵 苹果蓝',
        'primary': '#1C1C1E',
        'secondary': '#007AFF',
        'accent': '#30D158',
        'header_gradient': 'linear-gradient(135deg, #007AFF 0%, #5AC8FA 100%)',
        'footer_gradient': 'linear-gradient(135deg, #5AC8FA 0%, #007AFF 100%)'
    },
    'apple_green': {
        'name': '🟢 苹果绿',
        'primary': '#1C1C1E',
        'secondary': '#30D158',
        'accent': '#007AFF',
        'header_gradient': 'linear-gradient(135deg, #30D158 0%, #32D74B 100%)',
        'footer_gradient': 'linear-gradient(135deg, #32D74B 0%, #30D158 100%)'
    },
    'soft_sage': {
        'name': '🌿 鼠尾草',
        'primary': '#2D3748',
        'secondary': '#68D391',
        'accent': '#4FD1C7',
        'header_gradient': 'linear-gradient(135deg, #C6F6D5 0%, #9AE6B4 100%)',
        'footer_gradient': 'linear-gradient(135deg, #9AE6B4 0%, #C6F6D5 100%)'
    },
    'soft_lavender': {
        'name': '💜 淡紫',
        'primary': '#2D3748',
        'secondary': '#B794F6',
        'accent': '#F687B3',
        'header_gradient': 'linear-gradient(135deg, #FAF5FF 0%, #E9D8FD 100%)',
        'footer_gradient': 'linear-gradient(135deg, #E9D8FD 0%, #FAF5FF 100%)'
    },
    'apple_mint': {
        'name': '🌿 苹果薄荷',
        'primary': '#1C1C1E',
        'secondary': '#00C7BE',
        'accent': '#30D158',
        'header_gradient': 'linear-gradient(135deg, #00C7BE 0%, #32D74B 100%)',
        'footer_gradient': 'linear-gradient(135deg, #32D74B 0%, #00C7BE 100%)'
    },
    'soft_rose': {
        'name': '🌹 玫瑰金',
        'primary': '#2D3748',
        'secondary': '#F687B3',
        'accent': '#ED8936',
        'header_gradient': 'linear-gradient(135deg, #FED7E2 0%, #FBB6CE 100%)',
        'footer_gradient': 'linear-gradient(135deg, #FBB6CE 0%, #FED7E2 100%)'
    },
    
    # 商务专业配色
    'business_navy': {
        'name': '⚓ 商务海军蓝',
        'primary': '#1A202C',
        'secondary': '#2B6CB0',
        'accent': '#D69E2E',
        'header_gradient': 'linear-gradient(135deg, #2C5282 0%, #2B6CB0 100%)',
        'footer_gradient': 'linear-gradient(135deg, #2B6CB0 0%, #2C5282 100%)'
    },
    'business_charcoal': {
        'name': '⚫ 商务炭灰',
        'primary': '#1A202C',
        'secondary': '#4A5568',
        'accent': '#ED8936',
        'header_gradient': 'linear-gradient(135deg, #4A5568 0%, #718096 100%)',
        'footer_gradient': 'linear-gradient(135deg, #718096 0%, #4A5568 100%)'
    },
    'business_emerald': {
        'name': '💎 商务翡翠',
        'primary': '#1A202C',
        'secondary': '#38A169',
        'accent': '#D69E2E',
        'header_gradient': 'linear-gradient(135deg, #38A169 0%, #48BB78 100%)',
        'footer_gradient': 'linear-gradient(135deg, #48BB78 0%, #38A169 100%)'
    },
    'apple_purple': {
        'name': '🟣 苹果紫',
        'primary': '#1C1C1E',
        'secondary': '#AF52DE',
        'accent': '#FF9F0A',
        'header_gradient': 'linear-gradient(135deg, #AF52DE 0%, #BF5AF2 100%)',
        'footer_gradient': 'linear-gradient(135deg, #BF5AF2 0%, #AF52DE 100%)'
    },
    'apple_orange': {
        'name': '🟠 苹果橙',
        'primary': '#1C1C1E',
        'secondary': '#FF9F0A',
        'accent': '#007AFF',
        'header_gradient': 'linear-gradient(135deg, #FF9F0A 0%, #FFB340 100%)',
        'footer_gradient': 'linear-gradient(135deg, #FFB340 0%, #FF9F0A 100%)'
    },
    'apple_red': {
        'name': '🔴 苹果红',
        'primary': '#1C1C1E',
        'secondary': '#FF3B30',
        'accent': '#007AFF',
        'header_gradient': 'linear-gradient(135deg, #FF3B30 0%, #FF6961 100%)',
        'footer_gradient': 'linear-gradient(135deg, #FF6961 0%, #FF3B30 100%)'
    },
    'apple_indigo': {
        'name': '🟦 苹果靛蓝',
        'primary': '#1C1C1E',
        'secondary': '#5856D6',
        'accent': '#AF52DE',
        'header_gradient': 'linear-gradient(135deg, #5856D6 0%, #007AFF 100%)',
        'footer_gradient': 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)'
    },
    
    # 经典基础配色
    'classic': {
        'name': '经典蓝',
        'primary': '#2C3E50',
        'secondary': '#34495E',
        'accent': '#E74C3C',
        'header_gradient': 'linear-gradient(135deg, #2c3e50 0%, #4a6491 100%)',
        'footer_gradient': 'linear-gradient(135deg, #4a6491 0%, #2c3e50 100%)'
    },
    'ocean': {
        'name': '海洋蓝',
        'primary': '#0F4C75',
        'secondary': '#3282B8',
        'accent': '#BBE1FA',
        'header_gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'footer_gradient': 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
    },
    'sunset': {
        'name': '日落橙',
        'primary': '#FF6B6B',
        'secondary': '#FF8E53',
        'accent': '#4ECDC4',
        'header_gradient': 'linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%)',
        'footer_gradient': 'linear-gradient(135deg, #ffa726 0%, #ff6b6b 100%)'
    },
    'forest': {
        'name': '森林绿',
        'primary': '#2D5016',
        'secondary': '#4F7942',
        'accent': '#C9E265',
        'header_gradient': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        'footer_gradient': 'linear-gradient(135deg, #38ef7d 0%, #11998e 100%)'
    },
    'royal': {
        'name': '皇室紫',
        'primary': '#4A148C',
        'secondary': '#7B1FA2',
        'accent': '#FFD700',
        'header_gradient': 'linear-gradient(135deg, #8360c3 0%, #2ebf91 100%)',
        'footer_gradient': 'linear-gradient(135deg, #2ebf91 0%, #8360c3 100%)'
    },
    'aurora': {
        'name': '极光',
        'primary': '#1A237E',
        'secondary': '#3F51B5',
        'accent': '#00BCD4',
        'header_gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'footer_gradient': 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
    },
    'neon': {
        'name': '霓虹青',
        'primary': '#004D40',
        'secondary': '#00695C',
        'accent': '#FF4081',
        'header_gradient': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        'footer_gradient': 'linear-gradient(135deg, #38ef7d 0%, #11998e 100%)'
    },
    'sakura': {
        'name': '樱花粉',
        'primary': '#AD1457',
        'secondary': '#E91E63',
        'accent': '#4CAF50',
        'header_gradient': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'footer_gradient': 'linear-gradient(135deg, #f5576c 0%, #f093fb 100%)'
    },
    'midnight': {
        'name': '午夜蓝',
        'primary': '#0D1421',
        'secondary': '#1E3A8A',
        'accent': '#F59E0B',
        'header_gradient': 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        'footer_gradient': 'linear-gradient(135deg, #2a5298 0%, #1e3c72 100%)'
    },
    'golden': {
        'name': '黄金',
        'primary': '#B8860B',
        'secondary': '#DAA520',
        'accent': '#4A4A4A',
        'header_gradient': 'linear-gradient(135deg, #f7971e 0%, #ffd200 100%)',
        'footer_gradient': 'linear-gradient(135deg, #ffd200 0%, #f7971e 100%)'
    },
    'cosmos': {
        'name': '宇宙',
        'primary': '#1A1A2E',
        'secondary': '#16213E',
        'accent': '#E94560',
        'header_gradient': 'linear-gradient(135deg, #0c0c0c 0%, #667eea 100%)',
        'footer_gradient': 'linear-gradient(135deg, #667eea 0%, #0c0c0c 100%)'
    },
    'emerald': {
        'name': '翡翠绿',
        'primary': '#065F46',
        'secondary': '#059669',
        'accent': '#F59E0B',
        'header_gradient': 'linear-gradient(135deg, #134e5e 0%, #71b280 100%)',
        'footer_gradient': 'linear-gradient(135deg, #71b280 0%, #134e5e 100%)'
    },
    'crimson': {
        'name': '深红',
        'primary': '#7F1D1D',
        'secondary': '#991B1B',
        'accent': '#F59E0B',
        'header_gradient': 'linear-gradient(135deg, #c31432 0%, #240b36 100%)',
        'footer_gradient': 'linear-gradient(135deg, #240b36 0%, #c31432 100%)'
    },
    'platinum': {
        'name': '铂金灰',
        'primary': '#374151',
        'secondary': '#6B7280',
        'accent': '#3B82F6',
        'header_gradient': 'linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%)',
        'footer_gradient': 'linear-gradient(135deg, #2c3e50 0%, #bdc3c7 100%)'
    },
    'violet': {
        'name': '紫罗兰',
        'primary': '#5B21B6',
        'secondary': '#7C3AED',
        'accent': '#F59E0B',
        'header_gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'footer_gradient': 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
    },
    'coral': {
        'name': '珊瑚红',
        'primary': '#DC2626',
        'secondary': '#EF4444',
        'accent': '#06B6D4',
        'header_gradient': 'linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%)',
        'footer_gradient': 'linear-gradient(135deg, #feb47b 0%, #ff7e5f 100%)'
    },
    'glacier': {
        'name': '冰川蓝',
        'primary': '#0369A1',
        'secondary': '#0284C7',
        'accent': '#F59E0B',
        'header_gradient': 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
        'footer_gradient': 'linear-gradient(135deg, #66a6ff 0%, #89f7fe 100%)'
    },
    'lavender': {
        'name': '薰衣草',
        'primary': '#6366F1',
        'secondary': '#8B5CF6',
        'accent': '#10B981',
        'header_gradient': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
        'footer_gradient': 'linear-gradient(135deg, #fed6e3 0%, #a8edea 100%)'
    },
    'phoenix': {
        'name': '凤凰',
        'primary': '#B91C1C',
        'secondary': '#DC2626',
        'accent': '#F59E0B',
        'header_gradient': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
        'footer_gradient': 'linear-gradient(135deg, #fecfef 0%, #ff9a9e 100%)'
    }
}

# 新闻标签类型
NEWS_TAGS = {
    # 科技类
    'ai': {'name': 'AI工具', 'icon': 'fa-brain', 'color': '#1DA1F2'},
    'tech': {'name': '科技', 'icon': 'fa-laptop-code', 'color': '#673AB7'},
    'design': {'name': '设计', 'icon': 'fa-palette', 'color': '#FF9800'},
    'hardware': {'name': '硬件', 'icon': 'fa-memory', 'color': '#00C853'},
    'security': {'name': '安全', 'icon': 'fa-shield-alt', 'color': '#D32F2F'},
    'mobile': {'name': '移动', 'icon': 'fa-mobile-alt', 'color': '#9C27B0'},
    'web': {'name': 'Web', 'icon': 'fa-globe', 'color': '#2196F3'},
    'data': {'name': '数据', 'icon': 'fa-database', 'color': '#4CAF50'},
    
    # 综合新闻类
    'politics': {'name': '政治', 'icon': 'fa-landmark', 'color': '#795548'},
    'finance': {'name': '财经', 'icon': 'fa-chart-line', 'color': '#FF9800'},
    'military': {'name': '军事', 'icon': 'fa-fighter-jet', 'color': '#607D8B'},
    'business': {'name': '商业', 'icon': 'fa-briefcase', 'color': '#3F51B5'},
    'social': {'name': '社会', 'icon': 'fa-users', 'color': '#E91E63'},
    'sports': {'name': '体育', 'icon': 'fa-futbol', 'color': '#4CAF50'},
    'entertainment': {'name': '娱乐', 'icon': 'fa-film', 'color': '#9C27B0'},
    'weather': {'name': '天气', 'icon': 'fa-cloud-sun', 'color': '#00BCD4'}
}

@app.route('/')
def index():
    return render_template('index.html', 
                         color_themes=COLOR_THEMES, 
                         news_tags=NEWS_TAGS)

@app.route('/upload_logo', methods=['POST'])
def upload_logo():
    if 'logo' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['logo']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 添加时间戳避免文件名冲突
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 转换为base64以便在HTML中直接使用
        with open(filepath, 'rb') as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        # 删除临时文件
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'data': f"data:image/{get_file_extension(file.filename)};base64,{encoded_string}"
        })
    
    return jsonify({'error': '不支持的文件格式'}), 400

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        
        # 验证必需字段
        required_fields = ['report_name', 'news_items']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 生成HTML内容
        html_content = generate_html(data)
        
        return jsonify({
            'success': True,
            'html': html_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export_image', methods=['POST'])
def export_image():
    try:
        data = request.json
        html_content = data.get('html_content')
        
        if not html_content:
            return jsonify({'error': '没有HTML内容'}), 400
        
        # 检查是否为打包环境，使用不同的导出方式
        if getattr(sys, 'frozen', False):
            # 打包环境：返回HTML内容让前端处理
            return jsonify({
                'success': True,
                'method': 'frontend',
                'html': html_content,
                'message': '即将在新窗口打开日报，请使用浏览器的打印功能保存为PDF或截图'
            })
        else:
            # 开发环境：使用Playwright生成图片
            image_path = generate_image_from_html(html_content)
            
            if image_path and os.path.exists(image_path):
                return send_file(image_path, 
                               as_attachment=True, 
                               download_name=f"日报_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                               mimetype='image/png')
            else:
                return jsonify({'error': '图片生成失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def generate_html(data):
    """根据用户输入生成HTML内容"""
    
    # 获取用户输入
    report_name = data.get('report_name', '日报')
    logo_data = data.get('logo_data', '')
    color_theme = data.get('color_theme', 'classic')
    custom_colors = data.get('custom_colors', {})
    news_items = data.get('news_items', [])
    signature = data.get('signature', '精心策展，高效传达 - 洞察科技未来')
    show_creator = data.get('show_creator', True)
    
    # 获取颜色配置
    if color_theme == 'custom' and custom_colors:
        colors = custom_colors
    else:
        colors = COLOR_THEMES.get(color_theme, COLOR_THEMES['classic'])
    
    # 生成新闻条目HTML
    news_html = ""
    for i, item in enumerate(news_items, 1):
        tag_info = NEWS_TAGS.get(item.get('tag', 'tech'), NEWS_TAGS['tech'])
        
        news_html += f"""
        <div class="news-item">
            <div class="news-number">{i}</div>
            <div class="news-content">
                <div class="news-meta">
                    <span class="tag tag-{item.get('tag', 'tech')}">
                        <i class="fas {tag_info['icon']}"></i>{tag_info['name']}
                    </span>
                    <span class="company">
                        <i class="fas fa-building"></i>{item.get('company', '未知公司')}
                    </span>
                </div>
                <h3>{item.get('title', '标题')}</h3>
                <p>{item.get('description', '描述')}</p>
            </div>
        </div>
        """
    
    # 当前日期
    now = datetime.now()
    current_date = now.strftime('%Y年%m月%d日')
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    current_weekday = weekdays[now.weekday()]
    
    # 生成完整HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{report_name}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: {colors.get('primary', '#2C3E50')};
            --secondary: {colors.get('secondary', '#34495E')};
            --accent: {colors.get('accent', '#E74C3C')};
            --light: #ECF0F1;
            --dark: #2C3E50;
            --text: #333333;
            --text-light: #7F8C8D;
            --card-bg: #FFFFFF;
            --page-bg: #f5f7fa;
            --header-gradient: {colors.get('header_gradient', 'linear-gradient(135deg, #2c3e50 0%, #4a6491 100%)')};
            --footer-gradient: {colors.get('footer_gradient', 'linear-gradient(135deg, #4a6491 0%, #2c3e50 100%)')};
            --shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s ease;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            color: var(--text);
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            line-height: 1.6;
            min-height: auto;
            padding: 0.25rem;
            margin: 0;
            font-size: 16px;
        }}
        
        .container {{
            max-width: 750px;
            margin: 0 auto;
            padding: 0 0.5rem;
            width: 100%;
        }}
        
        /* 主要卡片容器 - 类似上传图片的效果 */
        .daily-report-card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            position: relative;
            margin: 0 auto;
            max-width: 100%;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        .daily-report-card::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--header-gradient);
            z-index: 1;
        }}
        
        /* 让卡片看起来更像上传的图片 */
        .daily-report-card::after {{
            content: "";
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
            border-radius: 22px;
            pointer-events: none;
            z-index: -1;
        }}
        
        /* 头部样式 */
        header {{
            background: var(--header-gradient);
            color: white;
            padding: 1.5rem 1.2rem;
            margin-bottom: 0;
            position: relative;
            overflow: hidden;
        }}
        
        header::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="rgba(255,255,255,0.05)"/></svg>');
            background-size: cover;
        }}
        
        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 2;
        }}
        
        .logo {{
            display: flex;
            align-items: center;
        }}
        
        .logo-image {{
            width: 50px;
            height: 50px;
            margin-right: 12px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent);
        }}
        
        .logo-text {{
            font-size: 2rem;
            font-weight: 300;
            letter-spacing: 1.5px;
        }}
        
        .logo-text span {{
            font-weight: 600;
            color: white;
        }}
        
        .header-right {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .date-display {{
            text-align: right;
            background: rgba(0, 0, 0, 0.2);
            padding: 0.8rem 1.5rem;
            border-radius: 30px;
        }}
        
        #current-date {{
            font-size: 1.2rem;
            font-weight: 500;
        }}
        
        #current-weekday {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        /* 主要内容区域 */
        .main-content {{
            margin-bottom: 0;
            padding: 1rem;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: var(--transition);
            margin-bottom: 0;
            border: none;
        }}
        
        .card-header {{
            padding: 1.4rem 1.8rem;
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--primary);
            color: white;
        }}
        
        .card-header-image {{
            width: 30px;
            height: 30px;
            margin-right: 10px;
            border-radius: 50%;
            object-fit: cover;
        }}
        
        .card-body {{
            padding: 1.2rem;
            background: white;
        }}
        
        .news-item {{
            padding: 2rem 0;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            align-items: flex-start;
            transition: all 0.2s ease;
        }}
        
        .news-item:hover {{
            background-color: rgba(52, 152, 219, 0.02);
            border-radius: 8px;
            margin: 0 -0.5rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}
        
        .news-item:last-child {{
            border-bottom: none;
        }}
        
        .news-number {{
            font-size: 2.2rem;
            font-weight: 900;
            color: var(--accent);
            margin-right: 1.8rem;
            min-width: 45px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.15);
            line-height: 1;
        }}
        
        .news-content {{
            flex: 1;
        }}
        
        .news-content p {{
            font-size: 1.15rem;
            line-height: 1.7;
            color: var(--text);
            margin-bottom: 0;
            font-weight: 450;
            text-align: justify;
            letter-spacing: 0.01em;
        }}
        
        .news-item h3 {{
            margin-bottom: 1.2rem;
            font-weight: 800;
            line-height: 1.25;
            color: var(--primary);
            font-size: 1.4rem;
            text-shadow: 0 1px 1px rgba(0,0,0,0.05);
        }}
        
        .news-meta {{
            font-size: 0.85rem;
            color: var(--text-light);
            display: flex;
            align-items: center;
            margin-bottom: 0.8rem;
            flex-wrap: wrap;
        }}
        
        .tag {{
            display: inline-flex;
            align-items: center;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 0.8rem;
            background-color: #eee;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }}
        
        .tag i {{
            margin-right: 5px;
        }}
        
        .tag-ai {{ background-color: #E8F4FD; color: #1DA1F2; }}
        .tag-tech {{ background-color: #F0EBF8; color: #673AB7; }}
        .tag-design {{ background-color: #FFF4E5; color: #FF9800; }}
        .tag-hardware {{ background-color: #E6F7ED; color: #00C853; }}
        .tag-security {{ background-color: #FFEBEE; color: #D32F2F; }}
        .tag-mobile {{ background-color: #F3E5F5; color: #9C27B0; }}
        .tag-web {{ background-color: #E3F2FD; color: #2196F3; }}
        .tag-data {{ background-color: #E8F5E8; color: #4CAF50; }}
        
        .company {{
            display: inline-flex;
            align-items: center;
            margin-right: 1rem;
            font-weight: 500;
        }}
        
        .company i {{
            margin-right: 5px;
            color: var(--accent);
        }}
        
        /* 底部样式 */
        footer {{
            background: var(--footer-gradient);
            color: white;
            padding: 1.2rem;
            text-align: center;
            margin-top: 0;
            position: relative;
        }}
        
        footer::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="rgba(255,255,255,0.05)"/></svg>');
            background-size: cover;
        }}
        
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 2;
        }}
        
        .signature {{
            font-style: italic;
            opacity: 0.8;
            display: flex;
            align-items: center;
        }}
        
        .signature::before {{
            content: "\\201C";
            font-size: 2rem;
            margin-right: 8px;
            color: var(--accent);
        }}
        
        /* 响应式设计 - 手机端优化 */
        @media (max-width: 768px) {{
            body {{
                font-size: 18px;
                line-height: 1.6;
                padding: 0.25rem;
            }}
            
            .container {{
                padding: 0 0.5rem;
                max-width: 100%;
            }}
            
            .daily-report-card {{
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                transform: translateY(0);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .daily-report-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
            }}
            
            header {{
                padding: 1.2rem 0.8rem;
                margin-bottom: 0;
            }}
            
            .header-content {{
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }}
            
            .header-right {{
                margin-top: 0;
                flex-direction: column;
            }}
            
            .logo-text {{
                font-size: 1.8rem;
                letter-spacing: 1px;
            }}
            
            .date-display {{
                text-align: center;
                padding: 0.6rem 1rem;
                font-size: 0.9rem;
            }}
            
            #current-date {{
                font-size: 1.2rem;
            }}
            
            #current-weekday {{
                font-size: 1rem;
            }}
            
            .main-content {{
                margin-bottom: 0;
                padding: 0.8rem;
            }}
            
            .card {{
                margin-bottom: 1rem;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
            }}
            
            .card-header {{
                padding: 1rem;
                font-size: 1.3rem;
            }}
            
            .card-body {{
                padding: 0.8rem;
            }}
            
            .news-item {{
                padding: 1rem 0;
                flex-direction: column;
                align-items: flex-start;
            }}
            
            .news-number {{
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
                margin-right: 0;
            }}
            
            .news-item h3 {{
                font-size: 1.6rem;
                margin-bottom: 1rem;
                line-height: 1.2;
                font-weight: 800;
                text-shadow: 0 1px 1px rgba(0,0,0,0.05);
            }}
            
            .news-meta {{
                flex-wrap: wrap;
                gap: 0.3rem;
                margin-bottom: 0.6rem;
            }}
            
            .tag {{
                font-size: 0.85rem;
                padding: 0.3rem 0.8rem;
                margin-right: 0.5rem;
                margin-bottom: 0.3rem;
            }}
            
            .company {{
                font-size: 1rem;
                margin-bottom: 0.3rem;
            }}
            
            .news-content p {{
                font-size: 1.3rem;
                line-height: 1.7;
                font-weight: 450;
                color: var(--text);
                text-align: justify;
                letter-spacing: 0.01em;
            }}
            
            footer {{
                padding: 1.2rem 0.8rem;
                margin-top: 0;
            }}
            
            .footer-content {{
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }}
            
            .signature {{
                font-size: 1.1rem;
                justify-content: center;
            }}
            
            .signature::before {{
                font-size: 1.5rem;
                margin-right: 6px;
            }}
        }}
        
        /* 超小屏幕优化 */
        @media (max-width: 480px) {{
            body {{
                padding: 0.25rem;
                font-size: 17px;
            }}
            
            .container {{
                padding: 0;
            }}
            
            .daily-report-card {{
                border-radius: 8px;
            }}
            
            header {{
                padding: 0.8rem 0.6rem;
            }}
            
            .main-content {{
                padding: 0.6rem;
            }}
            
            .logo-text {{
                font-size: 1.5rem;
            }}
            
            .card-header {{
                padding: 0.8rem;
                font-size: 1.2rem;
            }}
            
            .card-body {{
                padding: 0.6rem;
            }}
            
            .news-item h3 {{
                font-size: 1.5rem;
                font-weight: 800;
                line-height: 1.2;
                text-shadow: 0 1px 1px rgba(0,0,0,0.05);
            }}
            
            .tag {{
                font-size: 0.8rem;
                padding: 0.25rem 0.6rem;
            }}
            
            .company {{
                font-size: 0.95rem;
            }}
            
            .news-content p {{
                font-size: 1.25rem;
                line-height: 1.7;
                font-weight: 450;
                text-align: justify;
                letter-spacing: 0.01em;
            }}
            
            footer {{
                padding: 0.8rem 0.6rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="daily-report-card">
    <header>
                <div class="header-content">
            <div class="logo">
                {f'<img src="{logo_data}" alt="Logo" class="logo-image">' if logo_data else ''}
                <div class="logo-text"><span>{report_name if report_name.endswith('日报') else report_name + '日报'}</span></div>
            </div>
            <div class="header-right">
                <div class="date-display">
                    <div id="current-date">{current_date}</div>
                    <div id="current-weekday">{current_weekday}</div>
                </div>
            </div>
        </div>
    </header>
    
        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <div style="display: flex; align-items: center;">
                        <h2>今日内容</h2>
                    </div>
                    <div class="time">{now.strftime('%I:%M%p').lower()} 更新</div>
                </div>
                <div class="card-body">
                    {news_html}
            </div>
        </div>
    </div>
    
    <footer>
                <div class="footer-content">
            <div class="signature">{signature}</div>
            <div>
                        <div>© {now.year} {report_name if report_name.endswith('日报') else report_name + '日报'}</div>
                {f'<div style="font-size: 0.8rem; opacity: 0.7; margin-top: 0.5rem;">应用由靠谱瓦叔制作</div>' if show_creator else ''}
            </div>
        </div>
    </footer>
        </div>
    </div>
</body>
</html>
    """
    
    return html_template

def generate_image_from_html(html_content):
    """使用Playwright将HTML转换为图片"""
    try:
        # 检查是否为打包环境
        if getattr(sys, 'frozen', False):
            # 打包环境：返回错误提示
            raise Exception("打包版本暂不支持图片导出，请使用开发版本: python launcher.py")
        
        # 创建临时HTML文件
        temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_html.write(html_content)
        temp_html.close()
        
        # 生成唯一的图片文件名
        image_filename = f"report_{uuid.uuid4().hex}.png"
        image_path = os.path.join(tempfile.gettempdir(), image_filename)
        
        # 运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(capture_screenshot(temp_html.name, image_path))
        finally:
            loop.close()
        
        # 清理临时HTML文件
        os.unlink(temp_html.name)
        
        return image_path
        
    except Exception as e:
        print(f"生成图片时出错: {e}")
        return None

async def capture_screenshot(html_file_path, output_path):
    """异步截图函数"""
    try:
        # 检查是否为打包环境
        if getattr(sys, 'frozen', False):
            # 打包环境：使用系统安装的Playwright
            import subprocess
            import json
            
            # 获取系统Playwright路径
            try:
                result = subprocess.run(['playwright', '--version'], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception("Playwright未安装，请运行: playwright install chromium")
            except FileNotFoundError:
                raise Exception("Playwright未安装，请先安装Playwright: pip install playwright && playwright install chromium")
            
            # 使用系统Playwright进行截图
            cmd = [
                'playwright', 'screenshot',
                '--wait-for-selector', 'body',
                '--full-page',
                f'file://{html_file_path.replace(os.sep, "/")}',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"截图失败: {result.stderr}")
                
        else:
            # 开发环境：使用Python Playwright API
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # 设置视口大小
                await page.set_viewport_size({"width": 1200, "height": 800})
                
                # 加载HTML文件
                await page.goto(f"file://{html_file_path}")
                
                # 等待页面完全加载
                await page.wait_for_load_state("networkidle")
                
                # 截图
                await page.screenshot(path=output_path, full_page=True)
                
                await browser.close()
                
    except Exception as e:
        print(f"截图过程出错: {e}")
        raise e

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
