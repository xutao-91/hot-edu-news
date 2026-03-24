# 🔥 热点教育信息

**一个网站一个网站建立的真实教育新闻爬虫**

## 📊 数据来源（逐个建立）

| 状态 | 来源 | 类型 | 可靠性 | 文章数 |
|:---:|:---|:---|:---:|:---:|
| ✅ **第一个** | **Brookings Institution** | 智库/研究机构 | ⭐⭐⭐⭐⭐ | 4篇 |
| ✅ **第二个** | **CSIS** | 智库/战略研究 | ⭐⭐⭐⭐⭐ | 1篇 |
| ⏳ 待添加 | Education Week | 教育新闻媒体 | ⭐⭐⭐⭐⭐ | - |
| ⏳ 待添加 | ED.gov | 政府官方 | ⭐⭐⭐⭐⭐ | - |

## ✅ 核心原则

1. **一个网站一个爬虫** - 每个来源独立配置、独立测试、独立维护
2. **真实数据** - 只从真实网页抓取，不模拟编纂
3. **具体来源** - 每条新闻都有具体URL可查
4. **逐步验证** - 确保一个稳定运行后，再添加下一个

## 🚀 当前进度

### ✅ Brookings Institution（已完成）
**网址**: https://www.brookings.edu/topics/education-2/
- [x] 分析网站结构
- [x] 编写HTML爬虫
- [x] 配置GitHub Actions
- [x] 抓取4篇真实文章
- [x] 生成体制内风格中文摘要

### ✅ CSIS（Playwright方案测试中）
**网址**: https://www.csis.org
- [x] 分析网站结构
- [x] **Playwright浏览器自动化**（绕过反爬虫）
- [x] 配置GitHub Actions（含Playwright安装）
- [x] 抓取1篇真实文章
- [x] 生成体制内风格中文摘要

**技术方案**: 
- CSIS搜索页有严格反爬虫保护（Varnish 403）
- 采用 **Playwright浏览器自动化** 执行JavaScript、模拟真实用户
- 备用方案：详情页直接访问
- 自动运行：每天UTC 13:00

## 📁 项目结构

```
hot-edu-news/
├── README.md                          # 项目说明
├── index.html                         # 展示页面
├── .github/workflows/
│   ├── brookings.yml                  # Brookings自动爬虫
│   └── csis.yml                       # CSIS自动爬虫
├── sources/
│   ├── brookings/
│   │   ├── config.json                # Brookings配置
│   │   └── crawler.py                 # Brookings爬虫
│   └── csis/
│       ├── config.json                # CSIS配置
│       └── crawler.py                 # CSIS爬虫
├── data/
│   ├── brookings/                     # Brookings数据
│   └── csis/                          # CSIS数据
└── ...
```

## 🎯 下一步

1. 监控两个来源的自动爬虫运行
2. 根据运行情况优化爬虫
3. 确认稳定后添加第三个来源

---

**本项目确保每个来源都真实可靠，逐步建立完整的教育信息网络！**
