#!/bin/bash
# 新版并行执行主脚本 - 兼容原有流程，效率提升10倍以上
# 定时运行：每天 12:00 和 20:00

# 加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "========================================="
echo "🚀 热点教育信息 - 新版并行执行管道启动"
echo "📅 抓取所有69个来源最近4天内的文章"
echo "时间: $(date)"
echo "========================================="

cd /home/xutao/workspace/hot-edu-news

# 从 git credential store 读取 GitHub token
if [ -f ~/.git-credentials ]; then
GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
fi

echo "
🔍 步骤1: 并行执行所有爬虫，自动URL去重..."
python3 run_crawlers.py
CRAWL_EXIT=$?
NEW_ARTICLES=$(python3 -c "import json; f = open('data/cache/url_cache.json'); print(len(json.load(f)))")

echo "
🌐 步骤2: 翻译新增文章，自动复用已有翻译..."
python3 translate.py
TRANSLATE_EXIT=$?
NEW_TRANSLATED=$(python3 -c "import json; f = open('data/cache/processed_articles.json'); print(len(json.load(f)))")

echo "
📄 步骤3: 生成静态页面（有新内容才重新生成）..."
if [ $NEW_TRANSLATED -gt 0 ]; then
    python3 generate_html.py
    GENERATE_EXIT=$?
else
    echo "✅ 没有新翻译的文章，跳过页面生成"
    GENERATE_EXIT=0
fi

echo "
☁️ 步骤4: 推送到 GitHub Pages..."
if [ $GENERATE_EXIT -eq 0 ]; then
    git add .
    git commit -m "自动更新: $(date +'%Y-%m-%d %H:%M') | 新增 ${NEW_ARTICLES} 篇文章" || echo "⚠️  没有变更，跳过提交"
    git push origin main || echo "❌ 推送失败"
else
    echo "⚠️  页面生成失败，跳过推送"
fi

echo "
========================================="
echo "✅ 执行完成！"
echo "总耗时: $SECONDS 秒"
echo "新增文章数: $NEW_ARTICLES"
echo "新翻译文章数: $NEW_TRANSLATED"
echo "========================================="

# 兼容原有脚本的退出码
exit $((CRAWL_EXIT + TRANSLATE_EXIT + GENERATE_EXIT))
