#!/usr/bin/env python3
"""
CSIS 爬虫 - Playwright修复版本
解决超时问题，优化加载策略
"""
import json
import asyncio
from datetime import datetime
import os
import re

async def crawl_csis_async():
    """使用Playwright异步抓取CSIS - 修复超时问题"""
    print("🚀 启动Playwright浏览器...")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # 启动浏览器（无头模式）
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # 第一步：先访问首页建立session
            print("📡 步骤1：访问CSIS首页...")
            try:
                await page.goto('https://www.csis.org/', wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)
                print("✅ 首页加载完成")
            except Exception as e:
                print(f"⚠️  首页访问问题: {e}")
            
            # 第二步：访问搜索页（使用domcontentloaded而不是networkidle）
            url = "https://www.csis.org/search?archive=0&sort_by=relevance&f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport&f%5B2%5D=regions%3A801&keyword="
            print(f"📡 步骤2：访问搜索页...")
            
            try:
                # 使用domcontentloaded而不是networkidle，避免等待所有资源
                await page.goto(url, wait_until='domcontentloaded', timeout=45000)
                print("✅ 搜索页框架加载完成")
            except Exception as e:
                print(f"⚠️  搜索页加载问题: {e}")
                # 即使超时也继续，可能内容已加载
            
            # 等待JavaScript渲染内容
            print("⏳ 等待内容渲染...")
            await asyncio.sleep(5)  # 给JavaScript执行时间
            
            # 等待文章列表出现（最多等待30秒）
            try:
                await page.wait_for_selector('div.views-row', timeout=30000)
                print("✅ 文章列表出现")
            except Exception as e:
                print(f"⚠️  等待文章列表超时: {e}")
                # 截图查看页面状态
                await page.screenshot(path='/tmp/csis_screenshot.png')
                print("📸 已保存截图: /tmp/csis_screenshot.png")
            
            # 提取文章数据
            print("🔍 提取文章数据...")
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
                        if (text && text.length < 50 && !text.includes('and')) {
                            authors.push(text);
                        }
                    });
                    const author = authors.join(', ');
                    
                    // 日期 - 从contributors文本中提取
                    let date = '';
                    const contributorsDiv = article.querySelector('div.contributors');
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
            
            await browser.close()
            
            print(f"✅ 找到 {len(articles)} 篇文章")
            
            for i, article in enumerate(articles[:5], 1):
                print(f"\n  {i}. {article['title'][:60]}...")
                print(f"     👤 {article['author']}")
                print(f"     📅 {article['date']}")
            
            return articles
            
    except ImportError as e:
        print(f"❌ Playwright未安装: {e}")
        return None
    except Exception as e:
        print(f"❌ Playwright错误: {e}")
        import traceback
        traceback.print_exc()
        return None

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
        'crawl_method': 'playwright_fixed',
        'total_news': len(articles),
        'news': articles
    }
    
    filename = f"data/csis/{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已保存: {filename}")
    print(f"📊 共 {len(articles)} 条新闻")
    
    return output

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

def crawl_csis():
    """主函数"""
    print("="*60)
    print("🚀 CSIS爬虫启动 (Playwright修复版本)")
    print("="*60)
    
    articles = asyncio.run(crawl_csis_async())
    
    if articles and len(articles) > 0:
        return save_articles(articles)
    else:
        print("\n❌ 未获取到文章")
        return None

if __name__ == '__main__':
    result = crawl_csis()
    if result:
        print("\n🎉 爬虫成功完成！")
    else:
        print("\n❌ 爬虫失败")
        exit(1)
