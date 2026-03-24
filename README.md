# 🔥 热点教育信息

**一个网站一个网站建立的真实教育新闻爬虫**

## 📊 数据来源（逐个建立）

| 状态 | 来源 | 类型 | 可靠性 | 文章数 |
|:---:|:---|:---|:---:|:---:|
| ✅ **第一个** | **Brookings Institution** | 智库/研究机构 | ⭐⭐⭐⭐⭐ | 4篇 |
| ✅ **第二个** | **U.S. Department of Education** | 政府官方 | ⭐⭐⭐⭐⭐ | 10篇 |
| ✅ **第三个** | **The White House** | 政府官方 | ⭐⭐⭐⭐⭐ | 10篇 |
| ✅ **第四个** | **ACE** | 高等教育协会 | ⭐⭐⭐⭐⭐ | 10篇 |
| ⏳ 待添加 | Education Week | 教育新闻媒体 | ⭐⭐⭐⭐⭐ | - |

## ✅ 核心原则

1. **一个网站一个爬虫** - 每个来源独立配置、独立测试、独立维护
2. **真实数据** - 只从真实网页抓取，不模拟编纂
3. **具体来源** - 每条新闻都有具体URL可查
4. **逐步验证** - 确保一个稳定运行后，再添加下一个

## 🚀 当前进度

### ✅ Brookings Institution
**网址**: https://www.brookings.edu/topics/education-2/

### ✅ U.S. Department of Education
**网址**: https://www.ed.gov/about/news

### ✅ The White House
**网址**: https://www.whitehouse.gov/news/

### ✅ ACE (American Council on Education)
**网址**: https://www.acenet.edu/News-Room/Pages/default.aspx

**总计：34篇真实新闻**

## 📁 项目结构

```
hot-edu-news/
├── README.md
├── index.html
├── .github/workflows/          # 自动爬虫配置
│   ├── brookings.yml
│   ├── edgov.yml
│   ├── whitehouse.yml
│   └── ace.yml
├── sources/                    # 爬虫脚本
│   ├── brookings/
│   ├── edgov/
│   ├── whitehouse/
│   └── ace/
├── data/                       # 抓取数据
│   ├── brookings/
│   ├── edgov/
│   ├── whitehouse/
│   └── ace/
└── docs/                       # GitHub Pages部署
```

---

**本项目确保每个来源都真实可靠，逐步建立完整的教育信息网络！**
