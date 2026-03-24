# 🔥 热点教育信息 - 本地爬虫方案

## 架构变更：本地爬虫 + GitHub推送

**原因**: 
- CSIS等网站有严格反爬虫保护
- 本地机器可以正常访问网络
- 本地运行更稳定可控
- 避免GitHub Actions的IP限制

---

## 📋 本地环境配置

### 1. 系统要求
- Linux (Ubuntu/Debian)
- Python 3.8+
- Git
- 网络连接

### 2. 安装依赖（已安装）
```bash
# Chromium浏览器
apt-get install chromium-browser chromium-chromedriver

# Python依赖
pip install requests beautifulsoup4 --break-system-packages
```

---

## 🚀 运行方式

### 方式1：手动运行
```bash
cd /root/.openclaw/workspace/hot-edu-news

# 运行所有爬虫
bash run_local_crawler.sh

# 或单独运行
python3 sources/brookings/crawler.py
python3 sources/csis/crawler_local.py
```

### 方式2：定时自动运行（推荐）

**设置cron任务**:
```bash
# 编辑crontab
crontab -e

# 添加以下行（每天12:00和20:00运行）
0 12,20 * * * /bin/bash /root/.openclaw/workspace/hot-edu-news/run_local_crawler.sh >> /tmp/crawler.log 2>&1
```

---

## 📊 爬虫状态

| 来源 | 方式 | 状态 | 文章数 |
|:---|:---|:---:|:---:|
| Brookings | requests + BeautifulSoup | ✅ 正常 | 4篇 |
| CSIS | requests + URL列表 | ✅ 正常 | 1篇 |

---

## 🔧 新增文章方法

### 1. CSIS新增文章
编辑 `sources/csis/crawler_local.py`:
```python
'manual': [
    "https://www.csis.org/analysis/article-1",
    "https://www.csis.org/analysis/article-2",
    # 添加新URL
]
```

### 2. 自动发现URL（待开发）
- 从CSIS邮件订阅获取
- 从Twitter RSS获取
- 从其他聚合源导入

---

## 📝 日志查看

```bash
# 查看最新日志
tail -f /tmp/crawler.log

# 查看GitHub推送状态
cd /root/.openclaw/workspace/hot-edu-news && git log --oneline -5
```

---

## ✅ 优势

1. **稳定可靠** - 本地网络环境，不受GitHub限制
2. **实时更新** - 定时运行，及时获取新文章
3. **易于维护** - 直接编辑URL列表即可添加
4. **成本低** - 无需额外服务器或付费代理

---

## 🎯 下一步

1. 设置cron定时任务
2. 观察几天运行情况
3. 建立URL自动发现机制（邮件/Twitter等）
4. 考虑添加更多来源
