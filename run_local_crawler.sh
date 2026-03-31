#!/bin/bash
# 本地爬虫主控制脚本 - 只抓取最近4天的文章
# 定时运行：每天 12:00 和 20:00

echo "========================================"
echo "🚀 热点教育信息 - 本地爬虫启动"
echo "📅 只抓取最近4天内的文章"
echo "时间: $(date)"
echo "========================================"

cd /root/.openclaw/workspace/hot-edu-news

# 1. 运行Brookings爬虫
echo ""
echo "📰 [1/45] 运行 Brookings 爬虫..."
python3 sources/brookings/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Brookings 完成"
else
    echo "⚠️  Brookings 失败，继续..."
fi

# 2. 运行ED.gov爬虫
echo ""
echo "📰 [2/45] 运行 ED.gov 爬虫..."
python3 sources/edgov/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ ED.gov 完成"
else
    echo "⚠️  ED.gov 失败，继续..."
fi

# 3. 运行White House爬虫
echo ""
echo "📰 [3/45] 运行 White House 爬虫..."
python3 sources/whitehouse/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ White House 完成"
else
    echo "⚠️  White House 失败，继续..."
fi

# 4. 运行ACE爬虫
echo ""
echo "📰 [4/45] 运行 ACE 爬虫..."
python3 sources/ace/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ ACE 完成"
else
    echo "⚠️  ACE 失败，继续..."
fi

# 5. 运行NSF NCSES爬虫
echo ""
echo "📰 [5/45] 运行 NSF NCSES 爬虫..."
python3 sources/nsf_ncses/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ NSF NCSES 完成"
else
    echo "⚠️  NSF NCSES 失败，继续..."
fi

# 6. 运行Heritage爬虫
echo ""
echo "📰 [6/45] 运行 Heritage Foundation 爬虫..."
python3 sources/heritage/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Heritage 完成"
else
    echo "⚠️  Heritage 失败，继续..."
fi

# 7. 运行Rand爬虫
echo ""
echo "📰 [7/45] 运行 Rand Corporation 爬虫..."
python3 sources/rand/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Rand 完成"
else
    echo "⚠️  Rand 失败，继续..."
fi

# 8. 运行Pew Research爬虫
echo ""
echo "📰 [9/45] 运行 Pew Research 爬虫..."
python3 sources/pewresearch/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Pew Research 完成"
else
    echo "⚠️  Pew Research 失败，继续..."
fi

# 7. 同步docs目录
echo ""
echo "📂 [9/45] 同步 docs 目录..."
cp index.html docs/
cp -r data/ docs/
echo "✅ docs目录已同步"

# 6. 推送到GitHub
echo ""
echo "📤 推送到 GitHub..."
git add docs/ index.html README.md sources/ data/
git commit -m "📰 本地爬虫更新: $(date +'%Y-%m-%d %H:%M') - 只抓取最近3天" || echo "无变更"

# 使用token推送
if [ -n "$GITHUB_TOKEN" ]; then
    git remote set-url origin "https://xutao-91:${GITHUB_TOKEN}@github.com/xutao-91/hot-edu-news.git"
    git push origin main
    git remote set-url origin https://github.com/xutao-91/hot-edu-news.git
else
    echo "⚠️  GITHUB_TOKEN未设置，跳过推送"
fi

echo ""
echo "========================================"
echo "✅ 本地爬虫完成: $(date)"
echo "========================================"
