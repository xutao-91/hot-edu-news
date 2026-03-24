#!/root/.openclaw/workspace/hot-edu-news/venv/bin/python3
"""
CSIS 爬虫 - Selenium版本
使用Chrome浏览器自动化绕过反爬虫
"""
import json
from datetime import datetime
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawl_csis_selenium():
    """使用Selenium抓取CSIS"""
    print("="*60)
    print("🚀 CSIS爬虫启动 (Selenium版本)")
    print("="*60)
    print("🚀 启动Chrome浏览器...")
    
    try:
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 启动浏览器
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 第一步：访问首页
        print("📡 步骤1：访问CSIS首页...")
        driver.get('https://www.csis.org/')
        time.sleep(3)
        print("✅ 首页加载完成")
        
        # 第二步：访问搜索页
        url = "https://www.csis.org/search?archive=0&sort_by=relevance&f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport&f%5B2%5D=regions%3A801&keyword="
        print(f"📡 步骤2：访问搜索页...")
        driver.get(url)
        
        # 等待页面加载
        print("⏳ 等待页面加载...")
        time.sleep(5)
        
        # 等待文章列表
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.views-row"))
            )
            print("✅ 文章列表加载完成")
        except Exception as e:
            print(f"⚠️  等待文章列表超时: {e}")
        
        # 提取文章数据
        articles = []
        rows = driver.find_elements(By.CSS_SELECTOR, "div.views-row")
        
        print(f"✅ 找到 {len(rows)} 篇文章")
        
        for row in rows[:10]:  # 取前10篇
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
                    if text and len(text) < 50 and text not in ['and']:
                        authors.append(text)
                author = ', '.join(list(dict.fromkeys(authors)))  # 去重保持顺序
                
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
            return save_articles(articles, 'selenium')
        else:
            print("\n❌ 未获取到文章")
            return None
            
    except Exception as e:
        print(f"❌ Selenium错误: {e}")
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
    result = crawl_csis_selenium()
    if result:
        print("\n🎉 Selenium爬虫成功完成！")
    else:
        print("\n❌ Selenium爬虫失败")
        exit(1)
