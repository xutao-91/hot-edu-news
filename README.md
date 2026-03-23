# 🔥 热点教育信息

**一个网站一个网站建立的真实教育新闻爬虫**

## 📊 数据来源（逐个建立）

| 状态 | 来源 | 类型 | 可靠性 | 爬虫类型 |
|:---:|:---|:---|:---:|:---|
| 🚧 **第一个** | **Brookings Institution** | 智库/研究机构 | ⭐⭐⭐⭐⭐ | HTML解析 |
| ⏳ 待添加 | Education Week | 教育新闻媒体 | ⭐⭐⭐⭐⭐ | RSS |
| ⏳ 待添加 | ED.gov | 政府官方 | ⭐⭐⭐⭐⭐ | HTML解析 |
| ⏳ 待添加 | Chronicle | 高等教育 | ⭐⭐⭐⭐⭐ | RSS |

## ✅ 核心原则

1. **一个网站一个爬虫** - 每个来源独立配置、独立测试、独立维护
2. **真实数据** - 只从真实网页抓取，不模拟编纂
3. **具体来源** - 每条新闻都有具体URL可查
4. **逐步验证** - 确保一个稳定运行后，再添加下一个

## 🚀 当前进度

### Brookings Institution 爬虫（开发中）

**目标网址**: https://www.brookings.edu/topics/education-2/

- [x] 分析网站结构
- [x] 编写HTML爬虫
- [x] 配置GitHub Actions
- [ ] 首次抓取测试
- [ ] 验证数据真实性
- [ ] 您确认后添加第二个来源

### 技术细节

| 配置项 | 详情 |
|:---|:---|
| **目标URL** | https://www.brookings.edu/topics/education-2/ |
| **爬取方式** | HTML解析（Requests + BeautifulSoup） |
| **选择器** | article.card, .article-listing article |
| **更新频率** | 每天一次 |
| **数据保存** | `data/brookings/YYYY-MM-DD.json` |

## 📁 项目结构

```
hot-edu-news/
├── README.md                          # 项目说明
├── .github/workflows/
│   └── brookings.yml                  # Brookings自动爬虫
├── sources/
│   └── brookings/
│       ├── config.json                # 来源配置
│       └── crawler.py                 # 专用爬虫
├── data/
│   └── brookings/                     # Brookings数据
│       └── YYYY-MM-DD.json
└── ...
```

## 🎯 下一步

1. **测试 Brookings 爬虫** - 确保能成功抓取真实新闻
2. **验证数据** - 您检查数据来源和内容是否真实
3. **确认后添加第二个来源** - 如 Education Week 或 ED.gov

---

**本项目确保每个来源都真实可靠，逐步建立完整的教育信息网络！**
