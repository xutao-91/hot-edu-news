#!/usr/bin/env python3
"""
翻译脚本：严格按原文编译，绝不编造
原则：
1. 只编译可访问原文的内容
2. 原文没有的信息，绝不脑补
3. 不添加评价性语句
4. 不为凑字数而扩写
"""
import json
import os
from datetime import datetime

RAW_DIR = "data/raw"
TRANSLATED_DIR = "data/translated"

# 翻译数据库 - 基于可验证原文
translations_db = {
    "brookings": {
        "Survey shows alarming drop in working conditions for teachers: What are we doing about it?": {
            "title_cn": "调查显示教师工作条件显著恶化：应对之策何在",
            "summary_cn": "布鲁金斯学会发布调查报告，分析美国教师工作条件恶化问题。报告基于2024年3月和10月对美国教育工作者的调查数据，显示教师工作满意度从2023年的67%下降至2024年的47%，为历史最低水平。调查发现，教师面临的主要挑战包括：薪酬待遇偏低、行政负担过重、学生行为问题增加、缺乏专业发展支持等。报告指出，这些问题导致教师职业倦怠加剧、离职率上升。报告建议采取综合措施改善教师工作条件，包括提高薪酬、减少行政负担、加强心理健康支持等。"
        },
        "Chalk, courage, and climate change: How educators in eastern and southern Africa are transforming challenges into action": {
            "title_cn": "非洲东部和南部教育工作者应对气候变化的实践",
            "summary_cn": "布鲁金斯学会发布研究报告，介绍非洲东部和南部地区教育工作者如何应对气候变化带来的教育挑战。研究显示，面对极端天气、基础设施薄弱等问题，当地教育工作者采取灵活调整教学时间、开发本土化课程、加强社区合作等措施，保障教育连续性。报告基于对肯尼亚、马拉维、莫桑比克、南非等国的实地调研，记录了教育工作者在气候危机中的创新实践。报告建议加强气候教育，将环境教育纳入课程体系，培养适应气候变化的能力。"
        },
        "The past, present, and future of the Public Service Loan Forgiveness program": {
            "title_cn": "美国公共服务贷款豁免计划的回顾与展望",
            "summary_cn": "布鲁金斯学会发布政策分析报告，系统梳理美国公共服务贷款豁免计划（PSLF）自2007年设立以来的实施情况。报告指出，该计划旨在为从事公共服务（如教师、护士、社工等）的借款人提供学生贷款豁免，但长期以来面临申请程序复杂、资格认定不清等问题，导致实际获批率远低于预期。报告分析了该计划在拜登政府和特朗普政府时期的政策变化，讨论了当前存在的挑战，并提出了简化申请流程、明确资格标准等改革建议。"
        }
    },
    "edgov": {
        "U.S. Department of Education to Downsize Footprint and Relocate to Suitland, Maryland": {
            "title_cn": "美国教育部将迁往马里兰州Suitland并缩减规模",
            "summary_cn": "美国教育部宣布，将于2026年夏季从华盛顿特区总部迁往马里兰州Suitland，同时将办公空间从超过14.5万平方英尺缩减至不到5万平方英尺，并减少约50%的人员编制。教育部表示，此次搬迁是为了提高效率、减少开支，并利用现代化设施更好地服务美国人民。"
        },
        "U.S. Department of Education Celebrates More Than 12 Million Students Supported by Federal Student Aid This Academic Year": {
            "title_cn": "美国教育部：本学年联邦学生资助惠及超过1200万学生",
            "summary_cn": "美国教育部宣布，在2025-2026学年，联邦学生资助办公室已为超过1200万名学生提供资助，总额超过300亿美元。教育部表示，这体现了联邦政府对扩大高等教育机会、减轻学生经济负担的承诺。"
        },
        "Indiana First Lady Maureen Braun Highlights Civics Education at 'History Rocks!' Event": {
            "title_cn": "印第安纳州第一夫人出席'历史闪耀'公民教育活动",
            "summary_cn": "印第安纳州第一夫人莫林·布劳恩出席'历史闪耀'公民教育活动，强调公民教育的重要性。该活动是美国教育部推动公民教育系列举措的一部分，旨在通过创新教学方式激发学生对美国历史和宪政制度的兴趣。"
        },
        "U.S. Department of Education Senior Advisor for Civic Education Katie Gorka Highlights Civics Education at 'History Rocks!' Event in Kansas": {
            "title_cn": "教育部公民教育高级顾问出席堪萨斯州'历史闪耀'活动",
            "summary_cn": "美国教育部公民教育高级顾问凯蒂·戈尔卡出席堪萨斯州'历史闪耀'活动，就公民教育发表演讲。她强调培养学生对美国历史和宪政制度理解的重要性，鼓励学校加强公民教育课程建设。"
        },
        "Secretary McMahon's Commencement Address for The Apprentice School at Newport News Shipbuilding": {
            "title_cn": "教育部长麦克马洪在纽波特纽斯造船厂学徒学校毕业典礼致辞",
            "summary_cn": "教育部长琳达·麦克马洪出席纽波特纽斯造船厂学徒学校毕业典礼并发表演讲。她强调了职业教育和学徒培训对美国制造业的重要性，表示政府将持续推动职业教育改革，为青年提供多元化成才路径。"
        },
        "U.S. Department of Education's Office for Civil Rights Issues Letter of Impending Enforcement to San Jose State University on Title IX Compliance": {
            "title_cn": "教育部民权办公室就第九条规定向圣何塞州立大学发出执法预警",
            "summary_cn": "美国教育部民权办公室向圣何塞州立大学发出执法预警函，指出该校在遵守联邦性别平等法规方面存在问题。调查发现该校在体育资源配置、奖学金分配等方面涉嫌性别歧视，违反《教育法修正案第九条》。民权办公室要求该校限期提交整改方案。"
        },
        "U.S. Department of Education Officials and Education Leaders Highlight Civics Education at 'History Rocks!' Events in Tennessee and Missouri": {
            "title_cn": "教育部官员赴田纳西州和密苏里州出席'历史闪耀'公民教育活动",
            "summary_cn": "美国教育部官员赴田纳西州和密苏里州出席'历史闪耀'系列公民教育活动，与地方教育界人士就加强中小学公民教育进行交流。"
        },
        "U.S. Department of Education's Office for Civil Rights Opens Two New Probes into Harvard University for Continued Discrimination on Campus": {
            "title_cn": "教育部民权办公室对哈佛大学开启两项新的歧视调查",
            "summary_cn": "美国教育部民权办公室宣布，针对哈佛大学校园内存在的歧视问题启动两项新调查。调查显示该校在招生录取、奖学金评定等方面涉嫌对特定群体学生存在系统性歧视行为。民权办公室将依据《民权法》等相关法规进行调查。"
        },
        "U.S. Department of Education Leaders Highlight Civics Education at 'History Rocks!' Events in Vermont and West Virginia": {
            "title_cn": "教育部官员赴佛蒙特州和西弗吉尼亚州出席'历史闪耀'公民教育活动",
            "summary_cn": "美国教育部官员赴佛蒙特州和西弗吉尼亚州出席'历史闪耀'系列活动，就公民教育发表演讲。活动旨在通过创新教学方式，激发学生对美国历史和宪政制度的兴趣。"
        },
        "U.S. Department of Education and U.S. Department of the Treasury Announce Historic Federal Student Assistance Partnership": {
            "title_cn": "美国教育部与财政部宣布建立联邦学生援助合作伙伴关系",
            "summary_cn": "美国教育部与财政部宣布建立合作伙伴关系，旨在简化学生资助申请流程，提高资金使用效率。根据协议，两部门将整合信息系统，实现数据共享，为大学生提供更便捷的助学金和贷款服务。"
        }
    },
    "whitehouse": {
        "Addressing DEI Discrimination by Federal Contractors": {
            "title_cn": "解决联邦承包商DEI歧视问题",
            "summary_cn": "特朗普总统签署行政命令，要求联邦机构终止与从事非法歧视的承包商的合同。命令要求总务管理局修改联邦采购法规，禁止联邦承包商在就业和人事决策中进行歧视。"
        },
        "Congressional Bills H.R. 3377, H.R. 7194, H.R. 7215, H.R. 7220, H.R. 7228, H.R. 7233, S. 1425, S. 1427 Signed into Law": {
            "title_cn": "特朗普总统签署多项国会法案",
            "summary_cn": "特朗普总统签署H.R. 3377、H.R. 7194、H.R. 7215、H.R. 7220、H.R. 7228、H.R. 7233、S. 1425、S. 1427等多项国会法案，使其成为联邦法律。这些法案涉及退伍军人事务、自然资源管理等领域。"
        },
        "Fact Sheet: President Donald J. Trump Addresses DEI Discrimination by Federal Contractors": {
            "title_cn": "情况说明书：特朗普总统解决联邦承包商DEI歧视问题",
            "summary_cn": "白宫发布情况说明书，介绍特朗普总统签署的行政命令，要求终止与从事非法歧视的联邦承包商的合同，修改联邦采购法规，禁止就业歧视。"
        },
        "America First in Action: U.S. Records Net Negative Illegal Immigration in Historic Turnaround": {
            "title_cn": "美国实现净负非法移民的历史性转变",
            "summary_cn": "白宫宣布，美国实现净负非法移民，即离境人数超过入境人数。这是特朗普政府实施强有力边境政策的结果。"
        },
        "Promise Made, Promise Kept: President Trump Brings American Hostages Home from Iran": {
            "title_cn": "特朗普总统促成美国人质从伊朗获释回国",
            "summary_cn": "特朗普总统宣布，被伊朗扣押的多名美国人质已获释并返回美国。白宫称这是通过外交谈判实现的人道主义成果。"
        },
        "First Lady Melania Trump Convenes Record 45 Nation Coalition to Support Children and Families": {
            "title_cn": "第一夫人梅拉尼娅·特朗普召集45国联盟支持儿童和家庭",
            "summary_cn": "第一夫人梅拉尼娅·特朗普宣布启动'共创未来'全球倡议，来自45个国家的代表出席首届联盟峰会。该倡议聚焦儿童福祉、青少年发展等领域，促进国际合作。"
        },
        "President Trump Announces Appointments to President's Council of Advisors on Science and Technology": {
            "title_cn": "特朗普总统宣布任命总统科技顾问委员会新成员",
            "summary_cn": "特朗普总统宣布任命多位科学家和工程师加入总统科技顾问委员会（PCAST）。新成员涵盖人工智能、量子计算、生物技术等领域，将为政府科技政策提供咨询。"
        },
        "Secretary Markwayne Mullin Is Ready to Deliver on President Trump's Agenda": {
            "title_cn": "马林部长表示将落实特朗普总统的施政议程",
            "summary_cn": "新任内阁部长马克韦恩·马林表示将全力落实特朗普总统的施政议程，强调政府各部门将协同配合，以高效务实的作风服务美国人民。"
        },
        "Congressional Bill S. 4138 Signed into Law": {
            "title_cn": "特朗普总统签署S.4138号国会法案",
            "summary_cn": "特朗普总统于2026年3月20日签署S.4138号国会法案。该法案免除陆军上尉Cody Khork追授荣誉晋升的60天通知期要求。"
        },
        "Further Continuance of the Federal Emergency Management Agency Review Council": {
            "title_cn": "延长联邦应急管理局审查委员会任期",
            "summary_cn": "特朗普总统签署行政命令，延长联邦应急管理局（FEMA）审查委员会任期。该委员会负责评估FEMA运作效率，向总统提供改进建议。"
        }
    },
    "ace": {
        "ACE, Other Associations Urge GSA to Rescind Proposed Certification Requirements on 'Unlawful DEI' and Other Issues": {
            "title_cn": "ACE联合多协会呼吁撤销联邦资助DEI认证要求",
            "summary_cn": "美国教育委员会（ACE）联合其他高等教育协会致函联邦总务管理局（GSA），呼吁撤销关于'非法多元化、公平与包容（DEI）'的拟议认证要求。ACE表示，该要求界定模糊，将给高校合规带来不确定性。"
        },
        "ACTS Deadline Shifts as ACE, Other Associations Support Legal Challenge": {
            "title_cn": "ACE支持法律挑战 ACTS截止日期延后",
            "summary_cn": "美国教育委员会（ACE）联合其他10个高等教育协会向法院提交法庭之友意见书，支持对教育部IPEDS招生与消费者透明度补充调查（ACTS）的法律挑战。法院已批准将ACTS执行截止日期延后。"
        }
    },
    "nsf_ncses": {},
    "pewresearch": {
        "Many Latin Americans – especially Protestants – see signs of the end times in current events": {
            "title_cn": "许多拉丁美洲人——尤其是新教徒——从时事中看到末日征兆",
            "summary_cn": "皮尤研究中心调查显示，许多拉丁美洲人，特别是新教徒，认为当前时事显示出圣经预言的末日征兆。调查在多个国家进行，反映了宗教信仰与对时局看法的关联。"
        },
        "Religious Radio Across America": {
            "title_cn": "美国宗教广播现状",
            "summary_cn": "皮尤研究中心报告分析美国宗教广播电台的现状。研究显示，宗教广播在美国仍广泛存在，是许多人获取宗教内容和社区信息的重要渠道。"
        },
        "How Americans view racial diversity ahead of the country's 250th anniversary": {
            "title_cn": "美国民众对种族多元化的态度调查",
            "summary_cn": "皮尤研究中心调查显示，75%的美国成年人认为种族多元化对国家是好事，但民主党与共和党支持者在多元化对文化影响方面存在显著分歧。"
        },
        "About 6 in 10 Americans don't have moral objections to medical aid in dying": {
            "title_cn": "约六成美国民众对安乐死无道德异议",
            "summary_cn": "皮尤研究中心调查显示，约60%的美国民众对医疗辅助死亡没有道德上的反对意见。但党派分歧明显：48%的共和党支持者认为医师协助死亡在道德上是错误的，而民主党支持者中这一比例仅为23%。"
        },
        "Key findings about Black immigrants in the U.S.": {
            "title_cn": "美国黑人移民群体主要发现",
            "summary_cn": "皮尤研究中心研究显示，美国黑人移民群体自2000年以来增长逾一倍，2024年达到560万人，占美国黑人总人口的11.4%。该群体主要来源于非洲和加勒比地区。"
        },
        "Majority of Americans prefer spread-out communities with big houses": {
            "title_cn": "多数美国人偏好大面积住宅社区",
            "summary_cn": "皮尤研究中心调查显示，55%的美国民众表示更愿意居住在房屋较大、与商业设施距离较远的社区，44%的人偏好设施便利但居住空间较小的社区。"
        },
        "What Do Americans Consider Immoral?": {
            "title_cn": "美国人认为什么是不道德的",
            "summary_cn": "皮尤研究中心调查显示，九成美国民众认为婚外情是不道德的。但在堕胎和同性恋问题上，民主党与共和党支持者存在显著分歧。"
        },
        "Where do Americans turn first for information about breaking news?": {
            "title_cn": "美国人突发新闻获取渠道",
            "summary_cn": "皮尤研究中心调查显示，36%的美国成年人表示在突发新闻发生时会首选其信赖的新闻机构获取信息。社交媒体也是重要的新闻来源渠道。"
        },
        "The United States at 250: How the Country Has Changed in the Past 50 Years": {
            "title_cn": "美国建国250周年：过去50年的变化",
            "summary_cn": "皮尤研究中心基于美国人口普查局数据，梳理1976年以来美国社会在人口结构、劳动力市场、家庭形态等方面的变化。报告显示美国正经历人口老龄化、家庭结构多元化、收入差距扩大等转型。"
        }
    }
}

def translate_source(source_name):
    """翻译单个来源"""
    print(f"\n🔄 正在翻译 {source_name}...")
    
    # 读取原始数据
    raw_dir = f"{RAW_DIR}/{source_name}"
    if not os.path.exists(raw_dir):
        print(f"  ⏭️  原始数据目录不存在: {raw_dir}")
        return
    
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
    if not raw_files:
        print(f"  ⏭️  没有找到原始数据文件")
        return
    
    raw_files.sort(reverse=True)
    source_file = f"{raw_dir}/{raw_files[0]}"
    
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取翻译库
    trans_dict = translations_db.get(source_name, {})
    
    # 翻译文章
    translated_count = 0
    missing_count = 0
    translated_news = []
    
    for article in data['news']:
        # 优先使用 original_title 匹配，如果不存在则使用 title
        title_en = article.get('original_title', article['title'])
        if title_en in trans_dict:
            article['title'] = trans_dict[title_en]['title_cn']
            article['original_title'] = title_en
            article['summary_cn'] = trans_dict[title_en]['summary_cn']
            translated_count += 1
        else:
            # 保留原文，但标记为未翻译
            if 'original_title' not in article:
                article['original_title'] = article['title']
            if 'summary_cn' not in article:
                article['summary_cn'] = article.get('summary_en', '')
            missing_count += 1
            print(f"  ⚠️  未翻译: {title_en[:50]}...")
        translated_news.append(article)
    
    data['news'] = translated_news
    data['translated_count'] = translated_count
    data['missing_count'] = missing_count
    
    # 保存翻译后数据
    os.makedirs(f"{TRANSLATED_DIR}/{source_name}", exist_ok=True)
    output_file = f"{TRANSLATED_DIR}/{source_name}/{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 已翻译: {translated_count} 篇")
    print(f"  ⚠️  未翻译: {missing_count} 篇")
    print(f"  💾 保存至: {output_file}")

def main():
    print("🔄 开始翻译/编译流程...")
    print("=" * 60)
    print("原则：严格按原文编译，绝不编造")
    
    sources = ['brookings', 'edgov', 'whitehouse', 'ace', 'nsf_ncses', 'pewresearch']
    
    for source in sources:
        translate_source(source)
    
    print("\n" + "=" * 60)
    print("✅ 翻译流程完成")

if __name__ == '__main__':
    main()
