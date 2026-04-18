#!/bin/bash
# 本地爬虫主控制脚本 - 抓取所有69个来源的最近4天文章
# 定时运行：每天 12:00 和 20:00

echo "========================================"
echo "🚀 热点教育信息 - 本地全量爬虫启动"
echo "📅 抓取所有69个来源最近4天内的文章"
echo "时间: $(date)"
echo "========================================"

cd /home/xutao/workspace/hot-edu-news

# 从 git credential store 读取 GitHub token
if [ -f ~/.git-credentials ]; then
GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
fi

# 1. 运行Ace爬虫
echo ""
echo "📰 [1/69] 运行 Ace 爬虫..."
/usr/bin/python3 sources/ace/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Ace 完成"
else
    echo "⚠️  Ace 失败，继续..."
fi

# 2. 运行Anl News爬虫
echo ""
echo "📰 [2/69] 运行 Anl News 爬虫..."
/usr/bin/python3 sources/anl_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Anl News 完成"
else
    echo "⚠️  Anl News 失败，继续..."
fi

# 3. 运行Augie News爬虫
echo ""
echo "📰 [3/69] 运行 Augie News 爬虫..."
/usr/bin/python3 sources/augie_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Augie News 完成"
else
    echo "⚠️  Augie News 失败，继续..."
fi

# 4. 运行Bridgemi爬虫
echo ""
echo "📰 [4/69] 运行 Bridgemi 爬虫..."
/usr/bin/python3 sources/bridgemi/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Bridgemi 完成"
else
    echo "⚠️  Bridgemi 失败，继续..."
fi

# 5. 运行Brookings爬虫
echo ""
echo "📰 [5/69] 运行 Brookings 爬虫..."
/usr/bin/python3 sources/brookings/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Brookings 完成"
else
    echo "⚠️  Brookings 失败，继续..."
fi

# 6. 运行Butler Stories爬虫
echo ""
echo "📰 [6/69] 运行 Butler Stories 爬虫..."
/usr/bin/python3 sources/butler_stories/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Butler Stories 完成"
else
    echo "⚠️  Butler Stories 失败，继续..."
fi

# 7. 运行Daily Illini爬虫
echo ""
echo "📰 [7/69] 运行 Daily Illini 爬虫..."
/usr/bin/python3 sources/daily_illini/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Daily Illini 完成"
else
    echo "⚠️  Daily Illini 失败，继续..."
fi

# 8. 运行Ecampus News爬虫
echo ""
echo "📰 [8/69] 运行 Ecampus News 爬虫..."
/usr/bin/python3 sources/ecampus_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Ecampus News 完成"
else
    echo "⚠️  Ecampus News 失败，继续..."
fi

# 9. 运行Edgov爬虫
echo ""
echo "📰 [9/69] 运行 Edgov 爬虫..."
/usr/bin/python3 sources/edgov/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Edgov 完成"
else
    echo "⚠️  Edgov 失败，继续..."
fi

# 10. 运行Education Minnesota爬虫
echo ""
echo "📰 [10/69] 运行 Education Minnesota 爬虫..."
/usr/bin/python3 sources/education_minnesota/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Education Minnesota 完成"
else
    echo "⚠️  Education Minnesota 失败，继续..."
fi

# 11. 运行Elmhurst News爬虫
echo ""
echo "📰 [11/69] 运行 Elmhurst News 爬虫..."
/usr/bin/python3 sources/elmhurst_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Elmhurst News 完成"
else
    echo "⚠️  Elmhurst News 失败，继续..."
fi

# 12. 运行Heritage爬虫
echo ""
echo "📰 [12/69] 运行 Heritage 爬虫..."
/usr/bin/python3 sources/heritage/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Heritage 完成"
else
    echo "⚠️  Heritage 失败，继续..."
fi

# 13. 运行Hoover Research爬虫
echo ""
echo "📰 [13/69] 运行 Hoover Research 爬虫..."
/usr/bin/python3 sources/hoover_research/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Hoover Research 完成"
else
    echo "⚠️  Hoover Research 失败，继续..."
fi

# 14. 运行Iastate News爬虫
echo ""
echo "📰 [14/69] 运行 Iastate News 爬虫..."
/usr/bin/python3 sources/iastate_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Iastate News 完成"
else
    echo "⚠️  Iastate News 失败，继续..."
fi

# 15. 运行Iit News爬虫
echo ""
echo "📰 [15/69] 运行 Iit News 爬虫..."
/usr/bin/python3 sources/iit_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Iit News 完成"
else
    echo "⚠️  Iit News 失败，继续..."
fi

# 16. 运行Iu Education爬虫
echo ""
echo "📰 [16/69] 运行 Iu Education 爬虫..."
/usr/bin/python3 sources/iu_education/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Iu Education 完成"
else
    echo "⚠️  Iu Education 失败，继续..."
fi

# 17. 运行Iu News爬虫
echo ""
echo "📰 [17/69] 运行 Iu News 爬虫..."
/usr/bin/python3 sources/iu_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Iu News 完成"
else
    echo "⚠️  Iu News 失败，继续..."
fi

# 18. 运行Kelley爬虫
echo ""
echo "📰 [18/69] 运行 Kelley 爬虫..."
/usr/bin/python3 sources/kelley/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Kelley 完成"
else
    echo "⚠️  Kelley 失败，继续..."
fi

# 19. 运行Kettering News爬虫
echo ""
echo "📰 [19/69] 运行 Kettering News 爬虫..."
/usr/bin/python3 sources/kettering_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Kettering News 完成"
else
    echo "⚠️  Kettering News 失败，继续..."
fi

# 20. 运行Kstate News爬虫
echo ""
echo "📰 [20/69] 运行 Kstate News 爬虫..."
/usr/bin/python3 sources/kstate_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Kstate News 完成"
else
    echo "⚠️  Kstate News 失败，继续..."
fi

# 21. 运行Ku News爬虫
echo ""
echo "📰 [21/69] 运行 Ku News 爬虫..."
/usr/bin/python3 sources/ku_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Ku News 完成"
else
    echo "⚠️  Ku News 失败，继续..."
fi

# 22. 运行Mcw Cancer爬虫
echo ""
echo "📰 [22/69] 运行 Mcw Cancer 爬虫..."
/usr/bin/python3 sources/mcw_cancer/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Mcw Cancer 完成"
else
    echo "⚠️  Mcw Cancer 失败，继续..."
fi

# 23. 运行Mendoza爬虫
echo ""
echo "📰 [23/69] 运行 Mendoza 爬虫..."
/usr/bin/python3 sources/mendoza/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Mendoza 完成"
else
    echo "⚠️  Mendoza 失败，继续..."
fi

# 24. 运行Msoe爬虫
echo ""
echo "📰 [24/69] 运行 Msoe 爬虫..."
/usr/bin/python3 sources/msoe/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Msoe 完成"
else
    echo "⚠️  Msoe 失败，继续..."
fi

# 25. 运行Msu Today爬虫
echo ""
echo "📰 [25/69] 运行 Msu Today 爬虫..."
/usr/bin/python3 sources/msu_today/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Msu Today 完成"
else
    echo "⚠️  Msu Today 失败，继续..."
fi

# 26. 运行Mtu News爬虫
echo ""
echo "📰 [26/69] 运行 Mtu News 爬虫..."
/usr/bin/python3 sources/mtu_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Mtu News 完成"
else
    echo "⚠️  Mtu News 失败，继续..."
fi

# 27. 运行Ncses Data爬虫
echo ""
echo "📰 [27/69] 运行 Ncses Data 爬虫..."
/usr/bin/python3 sources/ncses_data/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Ncses Data 完成"
else
    echo "⚠️  Ncses Data 失败，继续..."
fi

# 28. 运行Nd News爬虫
echo ""
echo "📰 [28/69] 运行 Nd News 爬虫..."
/usr/bin/python3 sources/nd_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Nd News 完成"
else
    echo "⚠️  Nd News 失败，继续..."
fi

# 29. 运行Nd Science爬虫
echo ""
echo "📰 [29/69] 运行 Nd Science 爬虫..."
/usr/bin/python3 sources/nd_science/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Nd Science 完成"
else
    echo "⚠️  Nd Science 失败，继续..."
fi

# 30. 运行Nea News爬虫
echo ""
echo "📰 [30/69] 运行 Nea News 爬虫..."
/usr/bin/python3 sources/nea_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Nea News 完成"
else
    echo "⚠️  Nea News 失败，继续..."
fi

# 31. 运行Northwestern News爬虫
echo ""
echo "📰 [31/69] 运行 Northwestern News 爬虫..."
/usr/bin/python3 sources/northwestern_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Northwestern News 完成"
else
    echo "⚠️  Northwestern News 失败，继续..."
fi

# 32. 运行Notre Dame爬虫
echo ""
echo "📰 [32/69] 运行 Notre Dame 爬虫..."
/usr/bin/python3 sources/notre_dame/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Notre Dame 完成"
else
    echo "⚠️  Notre Dame 失败，继续..."
fi

# 33. 运行Nsf爬虫
echo ""
echo "📰 [33/69] 运行 Nsf 爬虫..."
/usr/bin/python3 sources/nsf/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Nsf 完成"
else
    echo "⚠️  Nsf 失败，继续..."
fi

# 34. 运行Nsf Ncses爬虫
echo ""
echo "📰 [34/69] 运行 Nsf Ncses 爬虫..."
/usr/bin/python3 sources/nsf_ncses/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Nsf Ncses 完成"
else
    echo "⚠️  Nsf Ncses 失败，继续..."
fi

# 35. 运行Oneill爬虫
echo ""
echo "📰 [35/69] 运行 Oneill 爬虫..."
/usr/bin/python3 sources/oneill/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Oneill 完成"
else
    echo "⚠️  Oneill 失败，继续..."
fi

# 36. 运行Pewresearch爬虫
echo ""
echo "📰 [36/69] 运行 Pewresearch 爬虫..."
/usr/bin/python3 sources/pewresearch/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Pewresearch 完成"
else
    echo "⚠️  Pewresearch 失败，继续..."
fi

# 37. 运行Pie News爬虫
echo ""
echo "📰 [37/69] 运行 Pie News 爬虫..."
/usr/bin/python3 sources/pie_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Pie News 完成"
else
    echo "⚠️  Pie News 失败，继续..."
fi

# 38. 运行Purdue爬虫
echo ""
echo "📰 [38/69] 运行 Purdue 爬虫..."
/usr/bin/python3 sources/purdue/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Purdue 完成"
else
    echo "⚠️  Purdue 失败，继续..."
fi

# 39. 运行Purdue Education爬虫
echo ""
echo "📰 [39/69] 运行 Purdue Education 爬虫..."
/usr/bin/python3 sources/purdue_education/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Purdue Education 完成"
else
    echo "⚠️  Purdue Education 失败，继续..."
fi

# 40. 运行Purdue Engineering爬虫
echo ""
echo "📰 [40/69] 运行 Purdue Engineering 爬虫..."
/usr/bin/python3 sources/purdue_engineering/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Purdue Engineering 完成"
else
    echo "⚠️  Purdue Engineering 失败，继续..."
fi

# 41. 运行Purdue Polytechnic爬虫
echo ""
echo "📰 [41/69] 运行 Purdue Polytechnic 爬虫..."
/usr/bin/python3 sources/purdue_polytechnic/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Purdue Polytechnic 完成"
else
    echo "⚠️  Purdue Polytechnic 失败，继续..."
fi

# 42. 运行Rand爬虫
echo ""
echo "📰 [42/69] 运行 Rand 爬虫..."
/usr/bin/python3 sources/rand/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Rand 完成"
else
    echo "⚠️  Rand 失败，继续..."
fi

# 43. 运行Rockhurst News爬虫
echo ""
echo "📰 [43/69] 运行 Rockhurst News 爬虫..."
/usr/bin/python3 sources/rockhurst_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Rockhurst News 完成"
else
    echo "⚠️  Rockhurst News 失败，继续..."
fi

# 44. 运行Showme Mizzou爬虫
echo ""
echo "📰 [44/69] 运行 Showme Mizzou 爬虫..."
/usr/bin/python3 sources/showme_mizzou/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Showme Mizzou 完成"
else
    echo "⚠️  Showme Mizzou 失败，继续..."
fi

# 45. 运行Slu News爬虫
echo ""
echo "📰 [45/69] 运行 Slu News 爬虫..."
/usr/bin/python3 sources/slu_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Slu News 完成"
else
    echo "⚠️  Slu News 失败，继续..."
fi

# 46. 运行Studlife爬虫
echo ""
echo "📰 [46/69] 运行 Studlife 爬虫..."
/usr/bin/python3 sources/studlife/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Studlife 完成"
else
    echo "⚠️  Studlife 失败，继续..."
fi

# 47. 运行Uchicago News爬虫
echo ""
echo "📰 [47/69] 运行 Uchicago News 爬虫..."
/usr/bin/python3 sources/uchicago_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uchicago News 完成"
else
    echo "⚠️  Uchicago News 失败，继续..."
fi

# 48. 运行Udmercy News爬虫
echo ""
echo "📰 [48/69] 运行 Udmercy News 爬虫..."
/usr/bin/python3 sources/udmercy_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Udmercy News 完成"
else
    echo "⚠️  Udmercy News 失败，继续..."
fi

# 49. 运行Uic Today爬虫
echo ""
echo "📰 [49/69] 运行 Uic Today 爬虫..."
/usr/bin/python3 sources/uic_today/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uic Today 完成"
else
    echo "⚠️  Uic Today 失败，继续..."
fi

# 50. 运行Uillinois News爬虫
echo ""
echo "📰 [50/69] 运行 Uillinois News 爬虫..."
/usr/bin/python3 sources/uillinois_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uillinois News 完成"
else
    echo "⚠️  Uillinois News 失败，继续..."
fi

# 51. 运行Uiowa Now爬虫
echo ""
echo "📰 [51/69] 运行 Uiowa Now 爬虫..."
/usr/bin/python3 sources/uiowa_now/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uiowa Now 完成"
else
    echo "⚠️  Uiowa Now 失败，继续..."
fi

# 52. 运行Umich Engineering爬虫
echo ""
echo "📰 [52/69] 运行 Umich Engineering 爬虫..."
/usr/bin/python3 sources/umich_engineering/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Umich Engineering 完成"
else
    echo "⚠️  Umich Engineering 失败，继续..."
fi

# 53. 运行Umich Ford爬虫
echo ""
echo "📰 [53/69] 运行 Umich Ford 爬虫..."
/usr/bin/python3 sources/umich_ford/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Umich Ford 完成"
else
    echo "⚠️  Umich Ford 失败，继续..."
fi

# 54. 运行Umich Isr爬虫
echo ""
echo "📰 [54/69] 运行 Umich Isr 爬虫..."
/usr/bin/python3 sources/umich_isr/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Umich Isr 完成"
else
    echo "⚠️  Umich Isr 失败，继续..."
fi

# 55. 运行Umich Medschool爬虫
echo ""
echo "📰 [55/69] 运行 Umich Medschool 爬虫..."
/usr/bin/python3 sources/umich_medschool/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Umich Medschool 完成"
else
    echo "⚠️  Umich Medschool 失败，继续..."
fi

# 56. 运行Umich Umsi爬虫
echo ""
echo "📰 [56/69] 运行 Umich Umsi 爬虫..."
/usr/bin/python3 sources/umich_umsi/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Umich Umsi 完成"
else
    echo "⚠️  Umich Umsi 失败，继续..."
fi

# 57. 运行Umn Cse爬虫
echo ""
echo "📰 [57/69] 运行 Umn Cse 爬虫..."
/usr/bin/python3 sources/umn_cse/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Umn Cse 完成"
else
    echo "⚠️  Umn Cse 失败，继续..."
fi

# 58. 运行Uni News爬虫
echo ""
echo "📰 [58/69] 运行 Uni News 爬虫..."
/usr/bin/python3 sources/uni_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uni News 完成"
else
    echo "⚠️  Uni News 失败，继续..."
fi

# 59. 运行Unl News爬虫
echo ""
echo "📰 [59/69] 运行 Unl News 爬虫..."
/usr/bin/python3 sources/unl_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Unl News 完成"
else
    echo "⚠️  Unl News 失败，继续..."
fi

# 60. 运行Uw Cdis爬虫
echo ""
echo "📰 [60/69] 运行 Uw Cdis 爬虫..."
/usr/bin/python3 sources/uw_cdis/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uw Cdis 完成"
else
    echo "⚠️  Uw Cdis 失败，继续..."
fi

# 61. 运行Uw Education爬虫
echo ""
echo "📰 [61/69] 运行 Uw Education 爬虫..."
/usr/bin/python3 sources/uw_education/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uw Education 完成"
else
    echo "⚠️  Uw Education 失败，继续..."
fi

# 62. 运行Uw Engineering爬虫
echo ""
echo "📰 [62/69] 运行 Uw Engineering 爬虫..."
/usr/bin/python3 sources/uw_engineering/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uw Engineering 完成"
else
    echo "⚠️  Uw Engineering 失败，继续..."
fi

# 63. 运行Uw Gradschool爬虫
echo ""
echo "📰 [63/69] 运行 Uw Gradschool 爬虫..."
/usr/bin/python3 sources/uw_gradschool/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uw Gradschool 完成"
else
    echo "⚠️  Uw Gradschool 失败，继续..."
fi

# 64. 运行Uw News爬虫
echo ""
echo "📰 [64/69] 运行 Uw News 爬虫..."
/usr/bin/python3 sources/uw_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uw News 完成"
else
    echo "⚠️  Uw News 失败，继续..."
fi

# 65. 运行Uw Socwork爬虫
echo ""
echo "📰 [65/69] 运行 Uw Socwork 爬虫..."
/usr/bin/python3 sources/uw_socwork/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Uw Socwork 完成"
else
    echo "⚠️  Uw Socwork 失败，继续..."
fi

# 66. 运行Washu Engineering爬虫
echo ""
echo "📰 [66/69] 运行 Washu Engineering 爬虫..."
/usr/bin/python3 sources/washu_engineering/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Washu Engineering 完成"
else
    echo "⚠️  Washu Engineering 失败，继续..."
fi

# 67. 运行Washu Source爬虫
echo ""
echo "📰 [67/69] 运行 Washu Source 爬虫..."
/usr/bin/python3 sources/washu_source/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Washu Source 完成"
else
    echo "⚠️  Washu Source 失败，继续..."
fi

# 68. 运行Wayne News爬虫
echo ""
echo "📰 [68/69] 运行 Wayne News 爬虫..."
/usr/bin/python3 sources/wayne_news/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Wayne News 完成"
else
    echo "⚠️  Wayne News 失败，继续..."
fi

# 69. 运行Whitehouse爬虫
echo ""
echo "📰 [69/69] 运行 Whitehouse 爬虫..."
/usr/bin/python3 sources/whitehouse/crawler.py
if [ $? -eq 0 ]; then
    echo "✅ Whitehouse 完成"
else
    echo "⚠️  Whitehouse 失败，继续..."
fi

# 翻译所有未编译文章
echo ""
echo "🔄 自动翻译未编译内容..."
/usr/bin/python3 translate.py

# 生成页面
echo ""
echo "📄 生成HTML页面..."
/usr/bin/python3 generate_html.py

# 推送GitHub
echo ""
echo "🚀 推送到GitHub Pages..."
git add .
git commit -m "自动爬虫更新：$(date +'%Y-%m-%d %H:%M')"
git push origin main

echo ""
echo "🎉 所有任务完成！"
