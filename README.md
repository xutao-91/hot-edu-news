# 🔥 热点教育信息

**一个网站一个网站建立的真实教育新闻爬虫**

## 📊 数据来源（逐个建立）

| 状态 | 来源 | 类型 | 可靠性 | 文章数 |
|:---:|:---|:---|:---:|:---:|
| ✅ **第一个** | **Brookings Institution** | 智库/研究机构 | ⭐⭐⭐⭐⭐ | 4篇 |
| ✅ **第二个** | **U.S. Department of Education** | 政府官方 | ⭐⭐⭐⭐⭐ | 10篇 |
| ✅ **第三个** | **The White House** | 政府官方 | ⭐⭐⭐⭐⭐ | 10篇 |
| ⏳ 待添加 | Education Week | 教育新闻媒体 | ⭐⭐⭐⭐⭐ | - |

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

### ✅ U.S. Department of Education（已完成）
**网址**: https://www.ed.gov/about/news
- [x] 分析网站结构
- [x] 编写HTML爬虫
- [x] 配置GitHub Actions
- [x] 抓取10篇真实文章
- [x] 生成体制内风格中文摘要

### ✅ The White House（已完成）
**网址**: https://www.whitehouse.gov/news/
- [x] 分析网站结构
- [x] 编写HTML爬虫
- [x] 配置GitHub Actions
- [x] 抓取10篇真实文章
- [x] 生成体制内风格中文摘要

## 📁 项目结构

```
hot-edu-news/
├── README.md                          # 项目说明
├── index.html                         # 展示页面
├── .github/workflows/
│   ├── brookings.yml                  # Brookings自动爬虫
│   ├── edgov.yml                      # ED.gov自动爬虫
│   └── whitehouse.yml                 # White House自动爬虫
├── sources/
│   ├── brookings/                     # Brookings配置+爬虫
│   ├── edgov/                         # ED.gov配置+爬虫
│   └── whitehouse/                    # White House配置+爬虫
├── data/
│   ├── brookings/                     # Brookings数据
│   ├── edgov/                         # ED.gov数据
│   └── whitehouse/                    # White House数据
└── docs/                              # GitHub Pages部署目录
```

## 🎯 下一步

1. 监控三个来源的自动爬虫运行
2. 根据运行情况优化爬虫
3. 确认稳定后添加第四个来源

---

**本项目确保每个来源都真实可靠，逐步建立完整的教育信息网络！**
