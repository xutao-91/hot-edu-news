#!/usr/bin/env python3
"""
CSIS 爬虫 - 终极反检测版本
使用stealth插件和真实用户行为模拟
"""
import json
from datetime import datetime
import os
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def random_delay(min_sec=1, max_sec=3):
    """随机延迟，模拟真实用户"""
    time.sleep(random.uniform(min_sec, max_sec))

def crawl_csis_ultimate():
    """终极反检测爬虫"""
    print("="*60)
    print("🚀 CSIS爬虫启动 (终极反检测版本)")
    print("="*60)
    
    try:
        # Chrome选项 - 最大化真实度
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # 新无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # 关键反检测参数
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        # 真实用户代理
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        
        # 语言和时间zone
        chrome_options.add_argument('--lang=en-US,en')
        chrome_options.add_argument('--timezone=America/New_York')
        
        # 实验性选项
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 创建浏览器
        print("🚀 启动Chrome浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # 执行CDP命令隐藏webdriver
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                window.chrome = { runtime: {} };
            '''
        })
        
        # 设置页面加载超时
        driver.set_page_load_timeout(60)
        
        # 第一步：访问Google（建立正常用户行为模式）
        print("📡 步骤1：访问Google...")
        driver.get('https://www.google.com/')
        random_delay(2, 4)
        print("✅ Google加载完成")
        
        # 第二步：访问CSIS首页
        print("📡 步骤2：访问CSIS首页...")
        driver.get('https://www.csis.org/')
        random_delay(3, 5)
        
        # 模拟鼠标移动（真实用户行为）
        actions = ActionChains(driver)
        try:
            element = driver.find_element(By.TAG_NAME, 'body')
            actions.move_to_element(element).perform()
            random_delay(1, 2)
        except:
            pass
        
        print("✅ CSIS首页加载完成")
        
        # 第三步：访问搜索页
        print("📡 步骤3：访问搜索页...")
        url = "https://www.csis.org/search?archive=0&sort_by=relevance&f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport&f%5B2%5D=regions%3A801&keyword="
        driver.get(url)
        
        # 等待JavaScript执行
        print("⏳ 等待页面渲染...")
        random_delay(5, 8)
        
        # 模拟滚动（触发懒加载）
        print("📜 模拟滚动...")
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {500 * (i+1)});")
            random_delay(1, 2)
        
        # 等待文章列表
        print("🔍 查找文章列表...")
        rows = []
        max_attempts = 5
        for attempt in range(max_attempts):
            rows = driver.find_elements(By.CSS_SELECTOR, "div.views-row")
            if len(rows) > 0:
                print(f"✅ 找到 {len(rows)} 篇文章")
                break
            print(f"  尝试 {attempt+1}/{max_attempts}...")
            random_delay(3, 5)
        
        if len(rows) == 0:
            # 保存页面源码和截图用于调试
            with open('/tmp/csis_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            driver.save_screenshot('/tmp/csis_final.png')
            print("⚠️  未找到文章，已保存调试信息")
            driver.quit()
            return None
        
        # 提取文章数据
        articles = []
        for row in rows[:15]:  # 取前15篇
            try:
                # 标题
                title_elem = row.find_element(By.CSS_SELECTOR, "h3.headline-sm a span")
                title = title_elem.text.strip()
                
                # 链接
                link_elem = row.find_element(By.CSS_SELECTOR, "h3.headline-sm a")
                href = link_elem.get_attribute('href')
                
                # 摘要
                try:
                    summary_elem = row.find_element(By.CSS_SELECTOR, "div.search-listing--summary p")
                    summary = summary_elem.text.strip()
                except:
                    summary = ""
                
                # 作者
                author_elems = row.find_elements(By.CSS_SELECTOR, "span.contributor--item")
                authors = []
                for a in author_elems:
                    text = a.text.strip()
                    if text and len(text) < 50:
                        authors.append(text)
                # 去重
                seen = set()
                unique_authors = []
                for a in authors:
                    if a not in seen:
                        unique_authors.append(a)
                        seen.add(a)
                author = ', '.join(unique_authors[:3])
                
                # 日期
                date = ""
                try:
                    contributors = row.find_element(By.CSS_SELECTOR, "div.contributors")
                    date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', contributors.text)
                    if date_match:
                        date = date_match.group(1)
                except:
                    pass
                
                if title and href:
                    articles.append({
                        'title': title,
                        'url': href,
                        'author': author,
                        'date': date,
                        'summary_en': summary,
                        'source': 'CSIS',
                        'category': categorize(title)
                    })
                    print(f"\n  ✅ {title[:50]}...")
                    print(f"     👤 {author}")
                    print(f"     📅 {date}")
                    
            except Exception as e:
                continue
        
        driver.quit()
        
        if articles:
            return save_articles(articles, 'selenium_stealth')
        else:
            print("\n❌ 未获取到文章")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_articles(articles, method):
    """保存文章"""
    os.makedirs('data/csis', exist_ok=True)
    
    output = {
        'source': 'CSIS - Center for Strategic and International Studies',
        'source_url': 'https://www.csis.org',
        'crawled_at': datetime.now().isoformat(),
        'crawl_method': method,
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
    """分类"""
    title_lower = title.lower()
    categories = {
        'china': ['china', 'chinese', 'beijing'],
        'technology': ['technology', 'tech', 'digital', 'ai'],
        'energy': ['energy', 'solar', 'climate', 'environment'],
        'security': ['security', 'defense', 'military'],
        'economy': ['economy', 'economic', 'trade', 'market']
    }
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return 'general'

if __name__ == '__main__':
    result = crawl_csis_ultimate()
    if result:
        print("\n🎉 爬虫成功完成！")
    else:
        print("\n❌ 爬虫失败")
        exit(1)
