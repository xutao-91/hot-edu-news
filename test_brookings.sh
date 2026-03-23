#!/bin/bash
# Brookings 爬虫测试脚本

echo "🧪 测试 Brookings Education 爬虫..."
echo ""

# 检查Python
echo "✓ Python版本:"
python3 --version

# 检查依赖
echo ""
echo "✓ 检查依赖..."
pip install requests beautifulsoup4 python-dateutil -q

# 运行爬虫测试
echo ""
echo "🚀 运行爬虫（测试模式）..."
cd /root/.openclaw/workspace/hot-edu-news
python3 sources/brookings/crawler.py

# 检查结果
echo ""
if [ -f "data/brookings/$(date +%Y-%m-%d).json" ]; then
    echo "✅ 数据文件已生成："
    cat "data/brookings/$(date +%Y-%m-%d).json" | head -30
else
    echo "❌ 数据文件未生成"
fi
