#!/bin/bash
cd /home/xutao/workspace/hot-edu-news

# 运行缺失的17个来源爬虫，抓取最近4天内容
sources=(
"anl_news"
"wayne_state_news"
"washu_engineering_news"
"wisc_engineering_news"
"northern_iowa_news"
"uic_news"
"studlife_news"
"slu_news"
"missouri_news"
"purdue_polytechnic_news"
"purdue_engineering_news"
"nd_science_news"
"mtu_news"
"msu_news"
"ku_news"
"kstate_news"
"iit_news"
)

total=${#sources[@]}
count=1

for source in "${sources[@]}"; do
    echo ""
    echo "📰 [$count/$total] 运行 $source 爬虫..."
    if [ -d "sources/$source" ]; then
        /usr/bin/python3 sources/$source/crawler.py
        if [ $? -eq 0 ]; then
            echo "✅ $source 抓取完成"
        else
            echo "⚠️  $source 抓取失败，继续..."
        fi
    else
        echo "❌ $source 爬虫不存在，跳过"
    fi
    count=$((count+1))
done

echo ""
echo "✅ 所有缺失来源爬虫运行完成"
