import json

# 直接根据URL匹配更新
updates = [
    {
        'source': 'brookings',
        'url': 'generation-ai-starts-early',
        'summary': "2026年4月1日消息，随着人工智能技术的快速发展，越来越多的AI应用正在进入幼儿的生活。从智能玩具到教育应用，这些技术正在改变儿童学习和玩耍的方式。本指南详细分析了各种AI技术对幼儿发展的影响，为家长和教育工作者提供了实用的建议，帮助他们更好地理解和引导儿童与AI的互动。"
    },
    {
        'source': 'brookings',
        'url': 'what-are-community-college-bachelors-degrees',
        'summary': "2026年3月31日消息，社区学院学士学位（CCB）正在成为美国高等教育的重要组成部分。本文研究了24个允许社区学院授予学士学位的州的数据，发现CCB毕业生比同校同专业的副学士学位持有者年收入高4,000-9,000美元，但比传统四年制大学毕业生低约2,000美元。护理和刑事司法领域的CCB毕业生与传统学士学位持有者收入相当，而计算机科学和工程技术领域的毕业生收入差距最大。CCB项目成本显著低于传统学士学位，为学生提供了获得四年制学位的经济实惠途径。"
    },
    {
        'source': 'pewresearch',
        'url': 'how-americans-view-trumps-handling-of-trade-and-tariffs',
        'summary': "2026年4月1日消息，皮尤研究中心最新调查显示，58%的美国成年人对特朗普的贸易政策决策能力不太有信心或完全没有信心，63%对关税政策处理缺乏信心。共和党人和民主党人在此问题上分歧明显：74%的共和党人对特朗普的贸易政策有信心，而民主党人中只有12%。调查发现，与2025年相比，美国人对与加拿大和墨西哥贸易关系的看法发生了变化，更多人认为美国从这些关系中受益。2025年，美国与墨西哥的贸易逆差首次超过中国，达到创纪录的1946亿美元。"
    },
    {
        'source': 'whitehouse',
        'url': 'president-trump-delivers-powerful-primetime-address-on-operation-epic-fury',
        'summary': "2026年4月1日消息，特朗普总统今晚向全国发表黄金时段讲话，介绍'史诗愤怒行动'的进展情况。仅在一个月内，美军就对伊朗政权——世界上主要的恐怖主义国家赞助者——实施了迅速、果断、压倒性的打击。特朗普总统强调，伊朗海军已被摧毁，空军陷入废墟，大多数恐怖分子领导人已被消灭，伊斯兰革命卫队的指挥和控制正在被摧毁。他回顾了自己从2015年宣布参选总统以来，始终誓言绝不允许伊朗拥有核武器。特朗普总统还提到，他在第一任期内击毙了卡西姆·苏莱曼尼将军，并终止了奥巴马的伊朗核协议。他表示，美国将通过'史诗愤怒行动'继续打击伊朗，直到所有军事目标完全实现，确保美国最终摆脱伊朗侵略的邪恶和核讹诈的威胁。"
    },
    {
        'source': 'whitehouse',
        'url': 'president-trumps-clear-and-unchanging-objectives-drive-decisive-success-against-iranian-regime',
        'summary': "2026年4月1日消息，白宫发布声明，强调特朗普总统领导下的'史诗愤怒行动'目标明确且始终如一：消灭伊朗的弹道导弹武器库和生产能力，消灭其海军，切断其对恐怖代理人的支持，确保这个世界上主要的恐怖主义国家赞助者永远无法获得核武器。声明列举了从3月2日至3月31日，总统、副总统万斯、国务卿卢比奥、国防部长赫格塞思、参谋长联席会议主席凯恩将军、中央司令部司令库珀海军上将等高层官员反复重申的上述核心目标。目前，伊朗常规军事力量已被有效摧毁，其海军不具备航行能力，战术战斗机无法飞行，导弹和无人机发射能力大幅下降。美国中央司令部表示，正在为实现军事目标取得不可否认的进展，消除伊朗以有意义的方式向境外投射力量的能力。"
    }
]

for upd in updates:
    source = upd['source']
    url_match = upd['url']
    summary = upd['summary']
    
    try:
        with open(f'data/translated/{source}/2026-04-02.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        found = False
        for article in data.get('news', []):
            if url_match in article.get('url', ''):
                article['summary_cn'] = summary
                found = True
                print(f"✅ {source}: {article['title'][:50]}...")
                break
        
        if found:
            with open(f'data/translated/{source}/2026-04-02.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            print(f"❌ {source}: 未找到 {url_match}")
    except Exception as e:
        print(f"❌ {source}: {e}")

print("\n✅ 更新完成")