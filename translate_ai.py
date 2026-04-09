#!/usr/bin/env python3
"""
AI 自动翻译脚本
使用 Kimi API 翻译新文章的标题和生成摘要
"""
import json
import os
import re
from datetime import datetime

RAW_DIR = "data/raw"
TRANSLATED_DIR = "data/translated"

def extract_text_from_html(html_content):
    """从 HTML 中提取纯文本"""
    # 简单的 HTML 标签移除
    text = re.sub(r'<[^>]+>', ' ', html_content)
    # 移除多余空白
    text = ' '.join(text.split())
    return text[:500] if text else ""  # 限制长度

def call_kimi_for_translation(title_en, content_preview=""):
    """调用 Kimi API 进行翻译和摘要生成"""
    import subprocess
    
    prompt = f"""请将以下英文教育新闻标题翻译成中文，并根据标题内容生成一个100字左右的中文摘要。

原文标题: {title_en}
内容预览: {content_preview[:200] if content_preview else "无"}

请按以下格式回复：
标题: [中文标题]
摘要: [中文摘要]

要求：
1. 标题翻译要准确、通顺，符合中文新闻标题风格
2. 摘要要概括文章核心内容，使用体制内公文风格
3. 日期统一用"2026年4月消息"格式
4. 不要添加评价性语句"""

    try:
        # 使用 hermes-agent 的 Kimi 配置
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', 
             'https://api.kimi.com/coding/v1/chat/completions',
             '-H', 'Content-Type: application/json',
             '-H', 'Authorization: Bearer ${KIMI_API_KEY}',
             '-d', json.dumps({
                 "model": "kimi-code",
                 "messages": [{"role": "user", "content": prompt}],
                 "temperature": 0.3
             })],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 解析响应
            title_match = re.search(r'标题[:：]\s*(.+?)(?:\n|$)', content)
            summary_match = re.search(r'摘要[:：]\s*(.+?)(?:\n|$)', content, re.DOTALL)
            
            title_cn = title_match.group(1).strip() if title_match else title_en
            summary_cn = summary_match.group(1).strip() if summary_match else f"2026年4月消息，{title_cn}。"
            
            return title_cn, summary_cn
    except Exception as e:
        print(f"    AI 翻译失败: {e}")
    
    # 失败时返回原文和简单摘要
    return title_en, f"2026年4月消息，{title_en}。"

def translate_source(source_name):
    """翻译单个来源"""
    print(f"\n🔄 正在翻译 {source_name}...")
    
    raw_dir = f"{RAW_DIR}/{source_name}"
    if not os.path.exists(raw_dir):
        print(f"  ⏭️  原始数据目录不存在: {raw_dir}")
        return
    
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
    if not raw_files:
        print(f"  ⏭️  没有找到原始数据文件")
        return
    
    raw_files.sort(reverse=True)
    source_file = f"{raw_dir}/{raw_files[0]}"
    
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    translated_count = 0
    ai_translated_count = 0
    missing_count = 0
    translated_news = []
    
    for article in data['news']:
        title_en = article.get('original_title', article['title'])
        
        # 检查是否已有翻译
        if 'title_cn' in article and article['title_cn'] and article['title_cn'] != title_en:
            translated_count += 1
            translated_news.append(article)
            continue
        
        # 使用 AI 翻译
        print(f"  🤖 AI 翻译: {title_en[:50]}...")
        content_preview = article.get('content', '') or article.get('summary_en', '')
        title_cn, summary_cn = call_kimi_for_translation(title_en, content_preview)
        
        article['original_title'] = title_en
        article['title'] = title_cn
        article['summary_cn'] = summary_cn
        
        ai_translated_count += 1
        translated_news.append(article)
    
    data['news'] = translated_news
    data['translated_count'] = translated_count
    data['ai_translated_count'] = ai_translated_count
    data['missing_count'] = missing_count
    
    # 保存翻译后数据
    os.makedirs(f"{TRANSLATED_DIR}/{source_name}", exist_ok=True)
    output_file = f"{TRANSLATED_DIR}/{source_name}/{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 已有翻译: {translated_count} 篇")
    print(f"  🤖 AI 翻译: {ai_translated_count} 篇")
    print(f"  💾 保存至: {output_file}")

def main():
    print("🤖 开始 AI 自动翻译流程...")
    print("=" * 60)
    
    sources = ['brookings', 'edgov', 'whitehouse', 'ace', 'nsf_ncses', 'pewresearch', 'heritage', 'rand']
    
    for source in sources:
        translate_source(source)
    
    print("\n" + "=" * 60)
    print("✅ AI 翻译流程完成")

if __name__ == '__main__':
    main()
