#!/bin/bash
# 本地爬虫主控制脚本
# 定时运行：每天 12:00 和 20:00

echo "========================================"
echo "🚀 热点教育信息 - 本地爬虫启动"
echo "时间: $(date)"
echo "========================================"

cd /root/.openclaw/workspace/hot-edu-news

# 1. 运行Brookings爬虫
echo ""
echo "📰 [1/2] 运行 Brookings 爬虫..."
python3 sources/brookings/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Brookings 完成"
else
    echo "⚠️  Brookings 失败，继续..."
fi

# 2. 运行CSIS爬虫
echo ""
echo "📰 [2/2] 运行 CSIS 爬虫..."
timeout 180 python3 sources/csis/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ CSIS 完成"
else
    echo "⚠️  CSIS 失败，继续..."
fi

# 3. 推送到GitHub
echo ""
echo "📤 推送到 GitHub..."
git add data/ index.html README.md
git commit -m "📰 本地爬虫更新: $(date +'%Y-%m-%d %H:%M')" || echo "无变更"

# 使用token推送（从环境变量读取）
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
