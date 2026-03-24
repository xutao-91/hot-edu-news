#!/usr/bin/env python3
"""
CSIS (战略与国际研究中心) 爬虫 - Playwright版本
使用浏览器自动化绕过反爬虫保护
"""
import json
import asyncio
from datetime import datetime
import os
import re

# 异步运行Playwright
async def crawl_csis_async():
    """使用Playwright异步抓取CSIS"""
    print("🚀 启动Playwright浏览器...")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # 启动浏览器（无头模式）
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # 访问CSIS搜索页
            url = "https://www.csis.org/search?archive=0&sort_by=relevance&f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport&keyword="
            print(f"📡 访问: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # 等待内容加载
            await page.wait_for_selector('div.views-row', timeout=30000)
            
            print("✅ 页面加载完成，开始提取数据...")
            
            # 提取文章数据
            articles = await page.evaluate('''() => {
                const rows = document.querySelectorAll('div.views-row');
                const data = [];
                
                rows.forEach(row => {
                    const article = row.querySelector('article.report-search-listing');
                    if (!article) return;
                    
                    // 标题
                    const titleElem = article.querySelector('h3.headline-sm a span');
                    const title = titleElem ? titleElem.innerText.trim() : '';
                    
                    // 链接
                    const linkElem = article.querySelector('h3.headline-sm a');
                    const href = linkElem ? linkElem.getAttribute('href') : '';
                    const link = href ? 'https://www.csis.org' + href : '';
                    
                    // 摘要
                    const summaryElem = article.querySelector('div.search-listing--summary p');
                    const summary = summaryElem ? summaryElem.innerText.trim() : '';
                    
                    // 作者
                    const authorElems = article.querySelectorAll('span.contributor--item');
                    const authors = [];
                    authorElems.forEach(a => {
                        const text = a.innerText.trim();
                        if (text && !text.includes('and') && text.length < 50) {
                            authors.push(text);
                        }
                    });
                    const author = authors.join(', ');
                    
                    // 日期
                    const contributorsDiv = article.querySelector('div.contributors');
                    let date = '';
                    if (contributorsDiv) {
                        const text = contributorsDiv.innerText;
                        const match = text.match(/([A-Z][a-z]+ \d{1,2}, \d{4})/);
                        if (match) date = match[1];
                    }
                    
                    if (title && link) {
                        data.push({
                            title: title,
                            url: link,
                            author: author,
                            date: date,
                            summary_en: summary
                        });
                    }
                });
                
                return data;
            }''')
            
            print(f"✅ 找到 {len(articles)} 篇文章")
            
            for i, article in enumerate(articles[:5], 1):
                print(f"\n  {i}. {article['title'][:60]}...")
                print(f"     👤 {article['author']}")
                print(f"     📅 {article['date']}")
            
            await browser.close()
            
            return articles
            
    except ImportError:
        print("❌ Playwright未安装，使用备用方案...")
        return None
    except Exception as e:
        print(f"❌ Playwright错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def crawl_csis():
    """主函数"""
    print("="*60)
    print("🚀 CSIS爬虫启动 (Playwright版本)")
    print("="*60)
    
    # 尝试Playwright
    try:
        articles = asyncio.run(crawl_csis_async())
        if articles:
            return save_articles(articles)
    except Exception as e:
        print(f"Playwright失败: {e}")
    
    # 备用方案：使用已知URL列表
    print("\n🔄 切换到备用方案：使用已知URL列表...")
    return crawl_fallback()

def save_articles(articles):
    """保存文章数据"""
    os.makedirs('data/csis', exist_ok=True)
    
    # 添加分类
    for article in articles:
        article['source'] = 'CSIS'
        article['category'] = categorize(article['title'])
    
    output = {
        'source': 'CSIS - Center for Strategic and International Studies',
        'source_url': 'https://www.csis.org',
        'crawled_at': datetime.now().isoformat(),
        'crawl_method': 'playwright',
        'total_news': len(articles),
        'news': articles
    }
    
    filename = f"data/csis/{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已保存: {filename}")
    print(f"📊 共 {len(articles)} 条新闻")
    
    return output

def crawl_fallback():
    """备用方案：使用已知URL列表"""
    known_urls = [
        "https://www.csis.org/analysis/chinas-solar-industry-upheaval-effects-will-be-global"
    ]
    
    import requests
    from bs4 import BeautifulSoup
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    articles = []
    
    for url in known_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('h1').get_text().strip() if soup.find('h1') else ''
            
            authors = []
            seen = set()
            for elem in soup.find_all(['span', 'a'], class_=lambda x: x and 'contributor' in str(x).lower()):
                text = elem.get_text().strip()
                if text and text not in seen and len(text) < 50:
                    authors.append(text)
                    seen.add(text)
            author = ', '.join(authors[:3])
            
            date = ''
            text_content = soup.get_text()
            date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', text_content)
            if date_match:
                date = date_match.group(1)
            
            if title:
                articles.append({
                    'title': title,
                    'url': url,
                    'author': author,
                    'date': date,
                    'source': 'CSIS',
                    'category': categorize(title)
                })
        except Exception as e:
            print(f"❌ {url}: {e}")
    
    if articles:
        return save_articles(articles)
    return None

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'china': ['china', 'chinese', 'beijing'],
        'technology': ['technology', 'tech', 'digital', 'ai', 'artificial intelligence'],
        'energy': ['energy', 'solar', 'climate', 'environment'],
        'security': ['security', 'defense', 'military'],
        'economy': ['economy', 'economic', 'trade', 'market']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

if __name__ == '__main__':
    crawl_csis()
