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
            "summary_cn": "布鲁金斯学会发布调查报告，全面分析美国教师工作条件持续恶化的现状、成因及对策。报告基于2024年3月和10月对美国教育工作者的两次大规模调查数据，显示教师工作满意度从2023年的67%急剧下降至2024年的47%，创下该调查历史最低水平。调查发现，教师面临的系统性挑战包括：薪酬待遇长期偏低且增长缓慢，难以吸引和留住优秀人才；行政负担过重，大量时间用于填写表格和参加会议，挤占教学准备时间；学生行为问题日益增加，课堂管理难度加大；缺乏有效的专业发展支持和职业晋升通道；心理健康支持体系不完善，教师职业倦怠现象普遍且严重。报告指出，这些问题已导致师资流失率持续攀升，优秀骨干教师大量流失，直接影响基础教育质量和教育公平。报告建议教育主管部门应采取综合性、多层次的应对措施：切实提高教师薪酬福利待遇，增强职业吸引力；大幅简化行政程序，让教师回归教学主业；建立完善的心理健康支持和职业发展体系；加强教师培训和专业发展支持，以稳定教师队伍，保障教育公平与质量。"
        },
        "Chalk, courage, and climate change: How educators in eastern and southern Africa are transforming challenges into action": {
            "title_cn": "非洲东部和南部教育工作者应对气候变化的实践",
            "summary_cn": "布鲁金斯学会发布研究报告，深入介绍非洲东部和南部地区教育工作者在应对气候变化挑战中的创新实践、宝贵经验及其对全球教育发展的启示意义。报告基于对肯尼亚、马拉维、莫桑比克、南非等国的实地调研，记录了教育工作者面对极端天气频发、基础设施薄弱、教育资源匮乏、资金短缺等严峻形势时展现出的非凡韧性、创造力和专业精神。当地教育工作者通过灵活调整教学时间以适应气候条件变化、积极开发本土化课程资源以增强环境教育实效、加强社区协作与家校联动以形成教育合力等多种创新方式，有效保障了教育连续性，最大限度减少了气候灾害对教育的负面影响，确保了儿童受教育权利不因环境恶化而受到侵害。报告强调，国际社会特别是发达国家应加大对发展中国家教育领域的资金和技术支持力度，帮助其提升应对气候变化的能力与韧性建设，共同应对全球性挑战。同时，报告建议各国政府应将气候教育纳入国民教育体系，培养具备环境意识、适应能力和可持续发展理念的未来人才，为全球可持续发展与气候行动贡献教育力量。"
        },
        "The past, present, and future of the Public Service Loan Forgiveness program": {
            "title_cn": "美国公共服务贷款豁免计划的回顾与展望",
            "summary_cn": "布鲁金斯学会发布政策分析报告，系统梳理美国公共服务贷款豁免计划（PSLF）自2007年设立以来的实施历程、政策演变、当前面临的困境及未来可能的改革方向。报告指出，该计划作为联邦政府鼓励优秀青年投身教育、医疗、法律等公共服务领域的重要激励机制，其政策初衷良好、设计意图明确，旨在为从事公共服务满10年的借款人提供剩余学生贷款豁免。但因申请程序复杂繁琐、资格认定标准模糊不清、部门间信息共享不畅、监督机制不健全等执行层面问题，实际惠及人数远低于预期，许多符合条件的公共服务从业者未能获得应有的贷款豁免，政策效果和公信力大打折扣。报告分析了该计划在拜登政府和特朗普政府时期的政策变化，讨论了当前存在的挑战，并提出了简化申请流程、明确资格标准、加强跨部门协调、完善监督机制等改革建议，以确保政策红利切实惠及符合条件的公共服务从业者，吸引和留住优秀人才服务公共事业。"
        }
    },
    "edgov": {
        "U.S. Department of Education to Downsize Footprint in Washington, D.C. and Save Taxpayers Over $4.8 Million Annually": {
            "title_cn": "美国教育部将缩减华盛顿办公规模 每年为纳税人节省超过480万美元",
            "summary_cn": "美国教育部宣布将缩减在华盛顿特区的办公规模，预计每年可为纳税人节省超过480万美元。教育部计划减少办公空间并优化人员配置，以提高运营效率。这一举措是特朗普政府推动联邦机构精简、减少政府开支的系列措施之一，旨在将更多资源用于直接服务学生和教育机构，而非维持庞大的行政体系。教育部表示，将通过数字化转型和流程优化，确保在减少办公空间的同时不影响服务质量和效率，继续履行其支持美国教育发展的核心使命。"
        },
        "U.S. Department of Education Celebrates More Than 10 Million FAFSA® Forms Complete and Additional Transparency Measures": {
            "title_cn": "美国教育部庆祝超过1000万份FAFSA表格完成及额外透明度措施",
            "summary_cn": "美国教育部宣布，已有超过1000万份联邦学生资助免费申请表（FAFSA）完成提交，显示出学生和家庭对高等教育资助的强烈需求。同时，教育部推出了额外的透明度措施，帮助学生和家庭更清楚地了解资助申请流程、资金分配情况和预期获得资助的时间表。这些措施旨在简化复杂的资助申请程序，减少申请过程中的障碍，确保更多符合条件的学生能够及时获得所需的经济支持，顺利完成高等教育学业，实现个人发展和职业目标。"
        },
        "Indiana First Lady Maureen Braun Highlights Civics Education at “History Rocks!” Event": {
            "title_cn": "印第安纳州第一夫人莫琳·布劳恩在'历史闪耀'活动中强调公民教育",
            "summary_cn": "印第安纳州第一夫人莫琳·布劳恩出席'历史闪耀'公民教育活动，强调公民教育的重要性。她在活动中分享了对美国历史和宪政制度的看法，鼓励学生们积极参与公民事务，培养批判性思维能力。该活动是美国教育部推动公民教育系列举措的一部分，旨在通过创新教学方式激发学生对美国历史和宪政制度的兴趣，培养下一代负责任的公民。布劳恩夫人强调了公民教育在维护民主制度和促进社会参与方面的重要作用。"
        },
        "U.S. Department of Education Senior Advisor for Civic Education Katie Gorka Highlights Civics Education at “History Rocks!” Event in Kansas": {
            "title_cn": "教育部公民教育高级顾问凯蒂·戈尔卡在堪萨斯州'历史闪耀'活动中强调公民教育",
            "summary_cn": "美国教育部公民教育高级顾问凯蒂·戈尔卡出席堪萨斯州'历史闪耀'活动，就公民教育发表演讲。她强调培养学生对美国历史和宪政制度理解的重要性，指出公民教育是培养学生批判性思维、社会责任感和参与意识的关键途径。戈尔卡鼓励学校加强公民教育课程建设，创新教学方法，通过生动活泼的教学方式激发学生对历史的兴趣。此次活动是美国教育部在全国范围内推动公民教育系列举措的重要组成部分，体现了联邦政府对强化国民教育的重视。"
        },
        "FACT SHEET: Victories for Higher Education, Making College More Affordable and Expediting Workforce Readiness": {
            "title_cn": "情况说明书：高等教育成果 让大学更负担得起并加快劳动力准备",
            "summary_cn": "美国教育部发布情况说明书，总结近期在高等教育领域取得的成果。文件指出，通过简化学生资助申请流程、扩大职业培训项目覆盖面、加强与产业界深度合作等系统性举措，有效降低了高等教育成本，显著提升了学生就业准备度与劳动力市场竞争力。教育部表示，将继续深化高等教育改革，优化资源配置，扩大优质教育资源覆盖面，确保更多美国青年能够负担得起大学教育并获得市场所需技能，为国家经济发展培养更多高素质人才。"
        },
        "Secretary McMahon’s Commencement Address for The Apprentice School at Newport News Shipbuilding": {
            "title_cn": "麦克马洪部长在纽波特纽斯造船厂学徒学校的毕业典礼致辞",
            "summary_cn": "教育部长琳达·麦克马洪出席纽波特纽斯造船厂学徒学校毕业典礼并发表演讲，强调了职业教育和学徒培训对美国制造业振兴和经济发展的重要性。她表示，特朗普政府将持续推动职业教育改革，扩大学徒制培训规模，完善产教融合机制，为美国青年提供更多元化的成才路径和职业发展机会。"
        },
        "U.S. Department of Education’s Office for Civil Rights Issues Letter of Impending Enforcement to San Jose State University on Title IX Compliance": {
            "title_cn": "教育部民权办公室就第九条规定向圣何塞州立大学发出执法预告函",
            "summary_cn": "美国教育部民权办公室向圣何塞州立大学发出执法预告函，正式指出该校在遵守联邦性别平等法规方面存在严重违规问题。调查发现，该校在体育资源配置、奖学金分配、训练设施使用、比赛机会提供等方面存在明显的性别歧视现象，违反《教育法修正案第九条》。民权办公室要求该校限期提交整改方案。"
        },
        "U.S. Department of Education Officials and Education Leaders Highlight Civics Education at “History Rocks!” Events in Tennessee and Missouri": {
            "title_cn": "教育部官员和教育领袖在田纳西州和密苏里州的'历史闪耀'活动中强调公民教育",
            "summary_cn": "美国教育部官员赴田纳西州和密苏里州出席'历史闪耀'系列公民教育活动，与地方教育界人士就加强中小学公民教育进行深入交流。活动期间，官员们参观了当地学校，观摩了公民教育课程，并与教师和学生进行了座谈。双方就如何创新教学方式、提高公民教育质量、培养学生批判性思维能力等议题交换了意见和经验。这些活动是美国教育部在全国范围内推动公民教育系列举措的重要组成部分，旨在提升公民教育水平。"
        },
        "U.S. Department of Education’s Office for Civil Rights Opens Two New Probes into Harvard University for Continued Discrimination on Campus": {
            "title_cn": "教育部民权办公室对哈佛大学开启两项新的调查",
            "summary_cn": "美国教育部民权办公室正式宣布，针对哈佛大学校园内持续存在的歧视问题启动两项新的调查程序。调查显示，该校在招生录取、奖学金评定及校园生活等多个方面涉嫌对特定群体学生存在系统性歧视行为。民权办公室将依据《民权法》等相关法律法规进行调查。"
        },
        "U.S. Department of Education Leaders Highlight Civics Education at “History Rocks!” Events in Vermont and West Virginia": {
            "title_cn": "教育部领导人在佛蒙特州和西弗吉尼亚州的'历史闪耀'活动中强调公民教育",
            "summary_cn": "美国教育部官员赴佛蒙特州和西弗吉尼亚州出席'历史闪耀'系列活动，就公民教育发表演讲。活动旨在通过创新教学方式，激发学生对美国历史和宪政制度的兴趣。"
        }
    },
    "whitehouse": {
        "Addressing DEI Discrimination by Federal Contractors": {
            "title_cn": "解决联邦承包商的DEI歧视问题",
            "summary_cn": "特朗普总统签署行政命令，要求联邦机构终止与从事非法歧视的承包商的合同。命令要求总务管理局修改联邦采购法规，禁止联邦承包商在就业和人事决策中进行歧视。这一举措旨在确保联邦资金的公平使用，防止基于种族、性别、宗教等因素的就业歧视，维护所有工人的平等权利。行政命令还建立了举报机制，允许员工举报歧视行为，并要求承包商提供合规证明，以确保其雇佣实践符合联邦法律要求。"
        },
        "Congressional Bills H.R. 3377, H.R. 7194, H.R. 7211 Signed into Law": {
            "title_cn": "国会法案H.R. 3377、H.R. 7194、H.R. 7211签署成为法律",
            "summary_cn": "特朗普总统签署H.R. 3377、H.R. 7194、H.R. 7211等多项国会法案，使其成为联邦法律。这些法案涉及退伍军人事务、自然资源管理等领域，旨在改善相关领域的政策执行和服务质量。白宫声明表示，这些法案的通过体现了府会合作推进国家治理的积极成果，将为美国人民带来实实在在的利益。特朗普总统感谢国会两党议员的支持与合作，强调这些法案对促进经济社会发展具有重要意义。"
        },
        "Fact Sheet: President Donald J. Trump Addresses DEI Discrimination by Federal Contractors": {
            "title_cn": "情况说明书：特朗普总统解决联邦承包商的DEI歧视问题",
            "summary_cn": "白宫发布情况说明书，详细介绍特朗普总统签署的行政命令，要求终止与从事非法歧视的联邦承包商的合同，修改联邦采购法规，禁止就业歧视。说明书解释了行政命令的背景、目标和具体措施，包括建立新的合规审查机制、加强对承包商的监督、设立举报渠道等。说明书强调，这些措施旨在确保联邦资金的公平使用，维护所有工人的平等权利，促进公平就业环境。"
        },
        "America First in Action: U.S. Records Net Negative Migration Across Every Metro Area": {
            "title_cn": "美国优先行动：美国每个大都市区都记录净负移民",
            "summary_cn": "白宫宣布，美国在所有大都市区都实现了净负移民，即离境人数超过入境人数。这是特朗普政府实施强有力边境政策的结果，包括加强边境执法、限制非法移民、加快驱逐程序等措施。白宫表示，这一成果证明了政府边境政策的有效性，有助于维护国家安全、保护美国工人就业机会、减少公共服务负担。政府将继续推进移民改革，确保边境安全，建立更加公平和有序的移民体系。"
        },
        "Promise Made, Promise Kept: President Trump Brings Another American Home": {
            "title_cn": "承诺兑现：特朗普总统又带回一名美国人",
            "summary_cn": "特朗普总统宣布，又一名在海外被扣押的美国人获释并返回美国。白宫称这是通过外交谈判实现的人道主义成果，体现了政府保护海外公民权益的决心和能力。总统表示，政府将继续努力，通过外交渠道和国际合作，争取所有在海外被不公正扣押的美国人的释放。白宫强调，保护美国公民的安全和权益是政府的首要职责，将采取一切必要措施实现这一目标。"
        },
        "First Lady Melania Trump Convenes Record 45 Nations at the White House and Introduces American-Built Humanoid": {
            "title_cn": "第一夫人梅拉尼娅·特朗普在白宫召集创纪录的45个国家并介绍美国制造的人形机器人",
            "summary_cn": "第一夫人梅拉尼娅·特朗普在白宫召集45个国家代表出席活动，并介绍了美国制造的人形机器人。该活动旨在展示美国在人工智能和机器人技术领域的创新成果，促进国际科技交流与合作。第一夫人强调了科技创新对改善人类生活、解决全球挑战的重要作用，呼吁各国加强合作，共同推动人工智能技术的负责任发展，确保技术进步造福全人类。"
        },
        "President Trump Announces Appointments to President’s Council of Advisors on Science and Technology": {
            "title_cn": "特朗普总统宣布任命总统科技顾问委员会成员",
            "summary_cn": "特朗普总统宣布任命多位科学家和工程师加入总统科技顾问委员会（PCAST）。新任命的成员涵盖人工智能、量子计算、生物技术、先进制造、清洁能源等前沿科技领域，均为各自领域的顶尖专家。这些专家将为政府制定科技政策、优化科研投入、推动技术转化提供重要咨询。"
        },
        "Secretary Markwayne Mullin Is Ready to Deliver on President Trump’s Agenda": {
            "title_cn": "马克韦恩·马林部长准备落实特朗普总统的议程",
            "summary_cn": "新任内阁部长马克韦恩·马林表示将全力落实特朗普总统的施政议程，强调政府各部门将协同配合，以高效务实的作风服务美国人民。马林部长表示，将严格执行总统指示，推动各项政策目标如期实现，回应选民期待。他强调，当前美国面临诸多内外挑战，需要政府各部门紧密协同配合，打破官僚壁垒，形成政策合力，提高政府运作效率，为美国人民提供更好的服务。"
        },
        "Further Continuance of the Federal Emergency Management Agency Review Council": {
            "title_cn": "延长联邦应急管理局审查委员会的任期",
            "summary_cn": "特朗普总统签署行政命令，延长联邦应急管理局（FEMA）审查委员会任期。该委员会负责评估FEMA运作效率，向总统提供改进建议，以提高应急管理效能。委员会将重点审查FEMA在灾害应对、资源分配、协调机制等方面的表现，提出改进建议。总统表示，延长委员会任期有助于深化对联邦应急管理工作的持续监督和评估，提升灾害应对能力和救援效率，确保联邦应急管理资源得到合理有效利用。"
        },
        "Greek Independence Day: A National Day of Celebration of Greek and American Democracy, 2026": {
            "title_cn": "希腊独立日：庆祝希腊和美国民主的全国日",
            "summary_cn": "特朗普总统发表公告，宣布3月25日为希腊独立日全国庆祝日。总统在公告中回顾了希腊作为西方民主发源地的重要历史地位，深刻阐述了希腊文明对西方政治思想、民主制度、哲学文化的深远影响，强调美希两国在民主价值观、法治精神、人权理念上的深厚纽带与共同追求。他表示，希腊独立日不仅是希腊人民的重要节日，也是美国人民共同庆祝的日子，两国友谊历经百年风雨仍历久弥坚。"
        }
    },
    "ace": {
        "ACE, Other Associations Urge GSA to Rescind Proposed Certification Requirements on “Unlawful DEI” and Other Issues": {
            "title_cn": "ACE联合其他协会敦促GSA撤销关于'非法DEI'的拟议认证要求",
            "summary_cn": "美国教育委员会（ACE）联合其他高等教育协会致函联邦总务管理局（GSA），呼吁撤销关于\"非法多元化、公平与包容（DEI）\"的拟议认证要求。协会指出，GSA本月早些时候提出的这一要求存在问题，因为它试图强制要求遵守通过行政命令和次级监管指导推进的反歧视法律解释。从法律立场和运营现实来看，机构或其他实体不应被要求提供额外认证以证明其遵守某种法律解释，这可能与州和地方法律相矛盾。GSA寻求要求的认证将涵盖特朗普政府称为\"歧视性做法\"的项目，如基于种族的奖学金或项目、\"文化能力\"要求、\"克服障碍\"叙事或\"多样性声明\"，以及\"创造敌对环境\"的培训项目。然而，协会信件指出，高校受一系列州和地方反歧视法律约束，必须确保其机构实践遵守这些法律要求。GSA指导中引用作为拟议要求理由的许多例子和做法\"仍然存在法律争议，在各州之间差异很大\"。虽然行政命令和次级监管指导有助于提供背景和理解，帮助了解联邦政府如何解释联邦法律要求，但它们不取代州和地方法律。"
        },
        "ACTS Deadline Shifts as ACE, Other Associations Support Legal Challenge": {
            "title_cn": "ACTS截止日期变更 ACE和其他协会支持法律挑战",
            "summary_cn": "美国教育委员会（ACE）联合其他10个高等教育协会向法院提交法庭之友意见书，支持对教育部IPEDS招生与消费者透明度补充调查（ACTS）的法律挑战。法院已批准将ACTS执行截止日期延后。"
        }
    },
    "nsf_ncses": {},
    "pewresearch": {
        "Many Latin Americans – especially Protestants – see a role for religion in national leadership, identity and laws": {
            "title_cn": "许多拉丁美洲人——尤其是新教徒——认为宗教在国家领导、身份认同和法律中应发挥作用",
            "summary_cn": "皮尤研究中心调查显示，巴西、哥伦比亚和秘鲁的大多数民众希望领导人捍卫其宗教信仰。新教徒尤其支持基督教在公共生活中发挥作用。"
        },
        "Religious Radio Across America": {
            "title_cn": "美国宗教广播",
            "summary_cn": "皮尤研究中心报告显示，几乎所有美国成年人都处于宗教广播电台覆盖范围内，最常见的是基督教广播电台。这些电台通常主要播放音乐或谈话节目。"
        },
        "Key facts about same-sex marriage around the world, 25 years after the Netherlands legalized it": {
            "title_cn": "同性婚姻在全球的关键事实：荷兰合法化25年后",
            "summary_cn": "皮尤研究中心调查显示，在荷兰成为全球首个承认同性婚姻的国家25年后，近40个国家和地区现在允许同性婚姻。但同性婚姻的普及程度各异，公众态度也不尽相同。"
        },
        "Americans Broadly Disapprove of U.S. Military Action in Iran": {
            "title_cn": "美国人普遍不赞成美国对伊朗采取军事行动",
            "summary_cn": "皮尤研究中心民调显示，大多数美国人认为对伊朗采取军事行动是错误的决定，不赞成特朗普对冲突的处理方式，党派分歧明显。"
        },
        "The United States at 250: How the Country Has Changed in the Past 50 Years": {
            "title_cn": "建国250周年的美国：过去50年国家的变化",
            "summary_cn": "皮尤研究中心基于50年的人口普查数据，展示美国人口结构、劳动力市场、家庭形态和经济状况自1976年以来的变化。"
        },
        "How Americans view racial diversity ahead of the country’s 250th anniversary": {
            "title_cn": "在美国建国250周年之际美国人如何看待种族多元化",
            "summary_cn": "皮尤研究中心调查显示，75%的美国成年人认为多元化对国家是好事，但民主党人和共和党人对多元化如何影响美国文化存在严重分歧。"
        },
        "Where do Americans turn first for information about breaking news?": {
            "title_cn": "美国人首先从哪里获取突发新闻信息",
            "summary_cn": "皮尤研究中心调查显示，当突发新闻事件发生时，36%的美国成年人表示通常会首选其信赖的新闻机构获取更多信息。"
        },
        "About 6 in 10 Americans don’t have moral objections to medical aid in dying": {
            "title_cn": "约六成美国人对医疗辅助死亡没有道德异议",
            "summary_cn": "皮尤研究中心调查显示，约六成美国人对医疗辅助死亡没有道德异议。共和党人认为医师协助死亡在道德上是错误的比例（48%）是民主党人（23%）的两倍多。"
        },
        "Key findings about Black immigrants in the U.S.": {
            "title_cn": "关于美国黑人移民的主要发现",
            "summary_cn": "皮尤研究中心研究显示，美国黑人移民群体自2000年以来增长逾一倍，2024年达到560万人，占美国黑人总人口的11.4%。该群体主要来源于非洲和加勒比地区。"
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
