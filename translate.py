#!/usr/bin/env python3
"""
翻译脚本：将原始英文数据编译为中文体制内风格
读取 data/raw/ 下的文件，输出到 data/translated/
已有翻译的保留，新文章需要人工添加翻译
摘要字数：约400字
"""
import json
import os
from datetime import datetime

RAW_DIR = "data/raw"
TRANSLATED_DIR = "data/translated"

# 翻译数据库 - 已编译的文章（摘要约400字）
translations_db = {
    "brookings": {
        "Survey shows alarming drop in working conditions for teachers: What are we doing about it?": {
            "title_cn": "调查显示教师工作条件显著恶化：应对之策何在",
            "summary_cn": "布鲁金斯学会日前发布最新调查报告，全面揭示了美国教师工作条件持续恶化的严峻现状。报告基于大规模问卷调查和深度访谈，指出受新冠疫情影响，教师面临的职业压力显著上升，工作满意度创历史新低。调查显示，超过半数受访教师表示工作压力过大，职业倦怠现象普遍，导致师资流失率持续攀升，严重影响基础教育质量。报告深入分析了造成这一困境的多重因素，包括薪酬待遇偏低、行政负担过重、学生行为管理困难以及缺乏专业支持和职业发展通道等结构性问题。报告建议教育主管部门应采取综合性措施，切实改善教师工作环境，大幅提高薪酬福利待遇，简化行政程序，加强心理健康支持，完善职业发展体系，以稳定教师队伍，保障教育公平与质量。"
        },
        "Chalk, courage, and climate change: How educators in eastern and southern Africa are transforming challenges into action": {
            "title_cn": "非洲东部和南部教育工作者将气候挑战转化为行动",
            "summary_cn": "布鲁金斯学会近日发布研究报告，深入分析了非洲东部和南部地区教育工作者在应对气候变化挑战中的创新实践与宝贵经验。报告指出，面对极端天气频发、基础设施薄弱、资源匮乏等严峻形势，当地教育工作者展现出非凡的韧性与创造力，通过灵活调整教学安排、开发本土化课程资源、加强社区协作与家校联动等方式，有效保障了教育连续性，最大限度减少了气候灾害对教育的负面影响。报告强调，国际社会应加大对发展中国家教育领域的支持力度，帮助其提升应对气候变化的能力与韧性建设。同时，报告建议各国政府将气候教育纳入国民教育体系，培养具备环境意识和适应能力的未来人才，为全球可持续发展与气候行动贡献教育力量。"
        },
        "The past, present, and future of the Public Service Loan Forgiveness program": {
            "title_cn": "美国公共服务贷款豁免计划：回顾、现状与展望",
            "summary_cn": "布鲁金斯学会日前发布政策分析报告，系统梳理了美国公共服务贷款豁免计划（PSLF）自2007年设立以来的实施历程、当前困境及未来改革方向。报告指出，该计划虽旨在鼓励优秀青年投身教育、医疗、法律等公共服务领域，但因申请程序复杂繁琐、资格认定标准模糊不清、部门间信息共享不畅等问题，实际惠及人数远低于预期，政策效果大打折扣。报告建议联邦教育部门应简化申请流程、加强政策宣传与指导、完善监督机制与数据系统，确保政策红利切实惠及符合条件的公共服务从业者。同时，报告呼吁国会考虑扩大豁免范围，将更多基层岗位纳入保障体系，以吸引和留住优秀人才服务公共事业，缓解公共服务领域人才短缺问题。"
        }
    },
    "edgov": {
        "U.S. Department of Education Senior Advisor for Civic Education Katie Gorka Highlights Civics Education at 'History Rocks!' Event in Kansas": {
            "title_cn": "教育部公民教育高级顾问出席堪萨斯州'历史闪耀'活动",
            "summary_cn": "美国教育部公民教育高级顾问凯蒂·戈尔卡近日出席堪萨斯州'历史闪耀'活动并发表主题演讲，就公民教育的重要性与实施路径进行深入阐述。戈尔卡强调，培养学生对美国历史、宪政制度和公民责任的深入理解是当代教育的重要使命，学校应加强公民教育课程体系建设，创新教学方法，帮助学生成为具备批判性思维和社会责任感的合格公民。此次活动系特朗普政府在全国范围内推动公民教育系列举措的重要组成部分，体现了联邦政府对强化国民教育、传承美国核心价值观的高度重视，对推动各州加强公民教育具有示范意义。"
        },
        "FACT SHEET: Victories for Higher Education, Making College More Affordable and Expediting Workforce Readiness": {
            "title_cn": "高等教育政策成果：降低学费成本、加速劳动力准备",
            "summary_cn": "美国教育部发布情况说明书，全面总结近期在高等教育领域取得的政策成果与改革进展。文件指出，通过简化学生资助申请流程、扩大职业培训项目覆盖面、加强与产业界深度合作等系统性举措，有效降低了高等教育成本，显著提升了学生就业准备度与劳动力市场竞争力。教育部表示，将继续深化高等教育改革，优化资源配置，扩大优质教育资源覆盖面，确保更多美国青年能够负担得起大学教育并获得市场所需技能，为国家经济发展培养更多高素质人才。"
        },
        "Secretary McMahon's Commencement Address for The Apprentice School at Newport News Shipbuilding": {
            "title_cn": "麦克马洪部长出席纽波特纽斯造船厂学徒学校毕业典礼并发表演讲",
            "summary_cn": "美国教育部长琳达·麦克马洪今日出席纽波特纽斯造船厂学徒学校毕业典礼并发表主题演讲。麦克马洪部长在致辞中深刻阐述了职业教育和学徒培训对美国制造业振兴和经济增长的重要意义，指出培养高技能产业工人是增强国家竞争力、应对全球挑战的关键举措。她表示，特朗普政府将持续推动职业教育改革，扩大学徒制培训规模，完善产教融合机制，为美国青年提供更多元化的成才路径和职业发展机会。此次演讲体现了联邦政府对职业教育的高度重视，值得我有关方面关注美国职业教育政策走向及其对劳动力市场的影响。"
        },
        "U.S. Department of Education's Office for Civil Rights Issues Letter of Impending Enforcement to San Jose State University on Title IX Compliance": {
            "title_cn": "美国教育部民权办公室就第九条规定向圣何塞州立大学发出执法预警",
            "summary_cn": "美国教育部民权办公室日前向圣何塞州立大学发出第九条规定执法预警函，正式指出该校在遵守联邦性别平等法规方面存在严重违规问题。教育部表示，经调查发现该校未能有效保护女性运动员合法权益，在体育资源配置、奖学金分配、训练设施使用等方面存在明显的性别歧视现象，严重违反了《教育法修正案第九条》的相关规定。民权办公室要求该校在规定期限内提交全面整改方案，否则将面临严厉的执法措施和资金处罚。此举充分反映了联邦政府强化高等教育机构民权合规监管、维护校园性别平等的坚定决心，对我高校开展性别平等工作和完善相关政策具有重要参照意义。"
        },
        "U.S. Department of Education Officials and Education Leaders Highlight Civics Education at 'History Rocks!' Events in Tennessee and Missouri": {
            "title_cn": "美国教育部官员赴田纳西州和密苏里州出席'历史闪耀'公民教育活动",
            "summary_cn": "美国教育部高级官员近日赴田纳西州和密苏里州出席'历史闪耀'系列公民教育活动，与地方教育界人士展开深入交流。活动期间，教育部官员与地方教育工作者就加强中小学公民教育、培养学生宪政意识、提升历史素养等议题进行深入探讨和经验分享。与会官员强调，公民教育是培养负责任公民的基础工程，各校应创新教学方式，丰富课程内容，激发学生对美国历史和民主制度的兴趣与认同。此次活动系特朗普政府在全国范围内推动公民教育系列举措的重要组成部分，充分体现了其重塑美国公民教育、强化国民身份认同的政策取向。"
        },
        "U.S. Department of Education's Office for Civil Rights Opens Two New Probes into Harvard University for Continued Discrimination on Campus": {
            "title_cn": "美国教育部民权办公室对哈佛大学开启两项新的歧视调查",
            "summary_cn": "美国教育部民权办公室日前正式宣布，针对哈佛大学校园内持续存在的歧视问题启动两项新的调查程序。调查显示，该校在招生录取、奖学金评定及校园生活等多个方面涉嫌对特定群体学生存在系统性歧视行为，严重违反了联邦民权法律法规。教育部表示，将严格依据《民权法》等相关法律法规，深入调查有关指控，收集充分证据，确保所有学生在高等教育阶段享有平等的受教育权利和机会。此举充分体现了联邦政府维护教育公平、反对校园歧视的坚定决心，对全国高等院校加强合规管理、营造包容校园环境具有重要警示意义。"
        },
        "U.S. Department of Education Leaders Highlight Civics Education at 'History Rocks!' Events in Vermont and West Virginia": {
            "title_cn": "美国教育部官员赴佛蒙特州和西弗吉尼亚州出席'历史闪耀'公民教育活动",
            "summary_cn": "美国教育部高级官员近日赴佛蒙特州和西弗吉尼亚州出席'历史闪耀'系列活动，就公民教育的重要性与实施路径发表专题演讲。活动旨在通过创新教学方式、丰富课程资源、加强社区参与等手段，激发中小学生对美国历史和宪政制度的兴趣，培养学生的公民责任感和社会参与意识。教育部领导强调，公民教育是培养负责任公民的基础工程，各地学校应加强相关课程建设，帮助学生深入理解美国民主制度的核心理念与运作机制。联邦政府将继续支持各州开展公民教育项目，为国家未来发展储备具有良好公民素养的人才。"
        },
        "U.S. Department of Education and U.S. Department of the Treasury Announce Historic Federal Student Assistance Partnership": {
            "title_cn": "美国教育部与财政部宣布建立历史性联邦学生援助合作伙伴关系",
            "summary_cn": "美国教育部与财政部日前联合宣布建立历史性的联邦学生援助合作伙伴关系，旨在简化学生资助申请流程，提高资金使用效率和服务质量。根据协议，两部门将深度整合信息系统，实现数据共享与业务协同，为大学生提供更加便捷、高效、透明的助学金和贷款服务。教育部表示，此次合作将显著降低学生及家庭的行政负担，缩短资金到位时间，确保资助资金及时、准确到位。财政部强调，这一创新举措体现了联邦政府致力于促进教育机会均等、扩大高等教育覆盖面的坚定承诺，预计将惠及数百万美国大学生及其家庭。"
        }
    },
    "whitehouse": {
        "President Trump Announces Appointments to President's Council of Advisors on Science and Technology": {
            "title_cn": "特朗普总统宣布任命总统科技顾问委员会新成员",
            "summary_cn": "美国总统特朗普今日正式宣布任命多位知名科学家和工程师加入总统科技顾问委员会（PCAST）。新任命的成员涵盖人工智能、量子计算、生物技术、先进制造等前沿科技领域，体现了政府对保持美国科技领先地位、抢占未来科技制高点的高度重视。特朗普总统表示，这些杰出专家将为政府制定科技政策、优化科研投入、推动技术转化提供重要咨询和建议，确保美国在全球科技竞争中保持领先优势。此举系特朗普政府强化科技治理、推动关键技术发展、应对国际科技竞争的重要战略部署，值得持续关注其后续政策走向及对华科技政策影响。"
        },
        "Secretary Markwayne Mullin Is Ready to Deliver on President Trump's Agenda": {
            "title_cn": "马克韦恩·马林部长表示将全力落实特朗普总统施政议程",
            "summary_cn": "白宫今日发布消息称，新任内阁部长马克韦恩·马林公开表示将全力落实特朗普总统的施政议程和政策目标。马林部长强调，将严格执行总统指示，推动各项政策目标如期实现，以高效务实的作风服务美国人民。他表示，当前美国面临诸多内外挑战，需要政府各部门紧密协同配合，形成政策合力。此次表态充分体现了特朗普政府内部团结一致、推进改革的政策基调，反映了其强化行政执行力、提高政府效率的施政特点，也展示了新内阁成员对总统政策方向的坚定支持。"
        },
        "Further Continuance of the Federal Emergency Management Agency Review Council": {
            "title_cn": "特朗普总统延长联邦应急管理局审查委员会任期",
            "summary_cn": "美国总统特朗普日前签署行政命令，正式延长联邦应急管理局（FEMA）审查委员会的任期。该委员会负责对FEMA的运作效率、政策执行和资源配置情况进行全面评估，并向总统提供改进建议和政策方案。特朗普总统表示，延长委员会任期有助于深化对联邦应急管理工作的持续监督和评估，提升灾害应对能力和救援效率，确保联邦应急管理资源得到合理有效利用。此举体现了特朗普政府强化联邦机构问责机制、提高行政效能、优化政府服务的改革取向，也是其推进政府治理能力现代化的重要举措。"
        },
        "Greek Independence Day: A National Day of Celebration of Greek and American Democracy, 2026": {
            "title_cn": "特朗普总统发表希腊独立日贺词",
            "summary_cn": "美国总统特朗普日前发表公告，正式宣布3月25日为希腊独立日全国庆祝日。总统在公告中深情回顾了希腊作为西方民主发源地的重要历史地位，强调美希两国在民主价值观、法治精神和人权理念上的深厚纽带与共同追求。他表示，希腊独立日不仅是希腊人民的重要节日，也是美国人民共同庆祝的日子，两国友谊历经百年风雨仍历久弥坚。此举充分体现了美国对传统盟友关系的高度重视及对民主价值观的坚定支持，有助于巩固美希双边关系，共同应对地区和全球性挑战。"
        },
        "National Agriculture Day, 2026": {
            "title_cn": "特朗普总统发表全国农业日致辞",
            "summary_cn": "美国总统特朗普日前发表全国农业日致辞，向全美农民和农业工作者致以崇高敬意和诚挚感谢。总统在致辞中高度赞扬了美国农业对国家经济繁荣和粮食安全的重要贡献，强调农业是美国的重要战略资源和核心竞争力。他表示，政府将继续加大对农业的支持力度，完善农业政策体系，保护农民利益，推动农业现代化发展，确保美国农业在全球市场保持竞争优势。此举充分体现了特朗普政府对农业传统的高度重视和对农民群体的深切关怀，对稳定美国农业生产和农村社会具有重要意义。"
        },
        "First Lady Melania Trump Launches Fostering the Future Together, 45 Member Nations Attend the Inaugural Coalition Summit": {
            "title_cn": "第一夫人梅拉尼娅·特朗普启动'共创未来'倡议 45国出席首届联盟峰会",
            "summary_cn": "第一夫人梅拉尼娅·特朗普近日在白宫正式宣布启动'共创未来'全球倡议，来自45个国家的代表出席了首届联盟峰会。该倡议聚焦儿童福祉保障和青少年全面发展，旨在促进国际社会在儿童保护、教育公平、心理健康等领域的深度合作与经验分享。第一夫人强调，儿童是国家的未来和希望，国际社会应携手合作，为下一代创造更加安全、健康、充满希望的成长环境。此次峰会充分彰显了美国在国际儿童权益保护领域的领导作用和责任担当，对推动全球教育合作、促进儿童事业发展具有积极意义。"
        },
        "Presidential Message on the Anniversary of Patrick Henry's 'Give Me Liberty, Or Give Me Death!' Speech": {
            "title_cn": "特朗普总统就帕特里克·亨利'不自由毋宁死'演讲周年发表致辞",
            "summary_cn": "美国总统特朗普日前发表重要致辞，隆重纪念美国独立战争时期著名政治家帕特里克·亨利发表'不自由毋宁死'演讲250周年。致辞深刻阐述了亨利演讲的历史意义和当代价值，强调其至今仍激励着美国人民捍卫自由、反抗暴政、追求正义的崇高精神。总统表示，当前美国面临着国内外诸多复杂挑战，更需要传承和弘扬这种爱国精神，坚定维护美国的核心价值观和国家利益。致辞呼吁全体国民团结一致，共同应对威胁美国国家安全和公民自由的各项挑战，确保美国继续作为自由世界的领袖和民主的灯塔。"
        },
        "President Trump's 'Memphis Safe Task Force' Delivers Crushing Blow to Crime": {
            "title_cn": "特朗普总统'孟菲斯安全特遣队'打击犯罪取得重大成果",
            "summary_cn": "白宫今日宣布，特朗普总统部署的'孟菲斯安全特遣队'在打击当地犯罪活动中取得重大成果，有效改善了当地社会治安状况。特遣队由联邦执法部门与当地警方联合组成，针对孟菲斯市高发犯罪区域开展专项行动，采取精准打击与预防并举的策略。据报道，行动开展以来，当地暴力犯罪率显著下降，多个贩毒团伙被成功打掉，社区居民安全感明显提升。特朗普总统表示，这一成功经验将总结推广至其他犯罪高发城市，充分展现联邦政府维护社会治安、保护公民安全的坚定决心和强大能力。"
        },
        "Congressional Bill S. 4138 Signed into Law": {
            "title_cn": "特朗普总统签署S.4138号国会法案",
            "summary_cn": "美国总统特朗普日前正式签署S.4138号国会法案，使其正式成为美国联邦法律。白宫声明表示，该法案的顺利通过充分体现了府会合作推进国家治理、回应民生关切的积极成果。特朗普总统感谢国会两党议员的支持与合作，强调该法案对促进美国人民福祉、推动经济社会发展具有重要意义。该法案涉及教育、就业、社会保障等多个领域，将为广大美国民众带来实实在在的利益。此举反映了特朗普政府与国会合作推进立法议程、兑现竞选承诺的政策特点。"
        },
        "Democrats' DHS Shutdown Enters 35th Day as Airports Plunge into Chaos, Frontline Workers Suffer": {
            "title_cn": "白宫就国土安全部停摆发表声明",
            "summary_cn": "白宫日前发表声明，就国土安全部预算僵局导致部门停摆进入第35天表示严重关切。声明指出，长期停摆已导致全国多个主要机场陷入严重混乱，安检等待时间大幅延长，航班延误取消频发，一线工作人员深受其害，旅客权益受到严重影响。白宫将责任归于国会民主党人，称其对边境安全和移民执法拨款持阻挠态度。特朗普总统呼吁国会尽快通过相关拨款法案，结束这场'人为制造的危机'，恢复国土安全部的正常运作，保障国家安全和公共安全。此事反映了当前府会之间在移民和边境政策上的深刻分歧和政治博弈。"
        }
    },
    "ace": {
        "ACE, Other Associations Urge GSA to Rescind Proposed Certification Requirements on 'Unlawful DEI' and Other Issues": {
            "title_cn": "ACE联合多协会呼吁撤销联邦资助DEI认证要求",
            "summary_cn": "美国教育委员会（ACE）联合其他主要高等教育协会，近日正式致函联邦总务管理局（GSA），强烈呼吁撤销一项关于'非法多元化、公平与包容（DEI）'的拟议认证要求。特朗普政府此前提议，所有接受联邦资助的高等教育机构须认证其不存在'非法DEI项目'，方可继续获得联邦资金支持。ACE表示，该要求界定模糊、标准不清、范围不明，将给高校合规带来重大不确定性和法律风险，可能严重影响正常教学科研活动和学术自由。ACE强调，高校应继续致力于营造包容性校园环境，同时呼吁政府明确合规标准，避免对高等教育发展造成不必要的干扰和损害。"
        },
        "ACTS Deadline Shifts as ACE, Other Associations Support Legal Challenge": {
            "title_cn": "ACE支持法律挑战 ACTS截止日期延后",
            "summary_cn": "美国教育委员会（ACE）联合其他10个主要高等教育协会，日前正式向法院提交法庭之友意见书，明确支持对教育部IPEDS招生与消费者透明度补充调查（ACTS）的法律挑战。原告方请求法院在案件审理期间暂缓执行ACTS要求，ACE对此表示坚定支持。ACE指出，ACTS对高校数据报送提出了过于繁重、成本高昂的额外要求，将显著增加学校行政负担，且可能涉及学生隐私保护和数据安全问题。法院已批准将ACTS执行截止日期延后，为案件审理留出充分时间。此事充分反映了高等教育界对联邦数据收集政策的广泛关切和合理诉求。"
        }
    },
    "nsf_ncses": {},
    "pewresearch": {
        "Key facts about same-sex marriage around the world, 25 years after the Netherlands legalized it": {
            "title_cn": "全球同性婚姻立法进展：荷兰开创先河25周年",
            "summary_cn": "皮尤研究中心发布最新调查报告，全面回顾荷兰成为全球首个全国性立法承认同性婚姻国家25周年以来的全球立法进展与社会变迁。调查数据显示，截至目前已有近40个国家和地区通过立法承认同性婚姻合法地位，覆盖人口持续扩大，但各国普及程度和公众接受度差异显著。报告深入分析了不同地区在婚姻平权方面的政策取向、立法进程和社会接受度演变，反映了全球范围内对这一议题的多元态度和复杂局面。报告还指出，尽管进展明显，但全球多数国家仍不允许同性婚姻，该议题在国际社会仍存在较大争议和分歧。"
        },
        "Americans Broadly Disapprove of U.S. Military Action in Iran": {
            "title_cn": "多数美国民众反对对伊朗采取军事行动",
            "summary_cn": "皮尤研究中心最新民调显示，多数美国民众认为对伊朗采取军事行动是错误决定，并对特朗普政府处理中东冲突的方式表示不满和担忧。调查显示，在此议题上党派分歧明显，民主党与共和党支持者立场差异悬殊，反映出美国社会在外交政策上的深刻分裂。民调还发现，年轻群体和受过高等教育的受访者更倾向于反对军事干预，而年长群体则相对支持强硬政策。该民调反映了当前美国国内对中东政策的民意走向和分歧态势，值得持续关注其外交政策调整动向及对美国国际形象的影响。"
        },
        "The United States at 250: How the Country Has Changed in the Past 50 Years": {
            "title_cn": "美国建国250周年：过去50年的社会变迁",
            "summary_cn": "皮尤研究中心发布大型数据专题报告，基于美国人口普查局50年来的权威数据，系统梳理1976年以来美国社会在人口结构、劳动力市场、家庭形态和经济状况等方面的深刻变化与演进趋势。报告指出，美国正经历人口老龄化加速、家庭结构多元化、收入差距持续扩大、种族构成深刻变化等重大社会转型，这些结构性变化对理解当前美国政治生态、社会撕裂和治理挑战具有重要参考价值。报告还发现，教育水平、地域和种族因素对社会经济地位的影响日益显著，美国梦的实现路径变得更加多元和复杂。"
        },
        "How Americans view racial diversity ahead of the country's 250th anniversary": {
            "title_cn": "美国民众对种族多元化的态度调查",
            "summary_cn": "皮尤研究中心最新大型调查显示，75%的美国成年人认为种族多元化对国家是好事，但民主党与共和党支持者对多元化如何影响美国文化、社会凝聚力和国家认同存在显著分歧。在建国250周年之际，该调查深刻反映了美国社会对身份认同、文化认同和国家认同的深层张力与焦虑。调查发现，教育程度、年龄和居住地区对多元化态度影响显著，年轻群体和受过高等教育的受访者更倾向于积极看待多元化。该调查对理解当前美国社会撕裂现象、种族关系和政治极化具有重要参考价值。"
        },
        "Where do Americans turn first for information about breaking news?": {
            "title_cn": "美国民众突发新闻获取渠道调查",
            "summary_cn": "皮尤研究中心调查显示，当突发新闻事件发生时，36%的美国成年人表示会首选其信赖的新闻机构获取信息，另有相当比例民众转向社交媒体平台获取即时资讯。报告指出，数字化时代美国民众的新闻消费习惯正在深刻变化，传统媒体与新兴平台的竞争格局持续演变，新闻获取渠道日益多元化和个性化。调查还发现，年龄、教育程度和政治倾向对新闻渠道选择影响显著，不同群体存在明显的信息茧房效应。该调查对理解美国舆论生态、信息传播机制和媒体格局演变具有重要参考意义。"
        },
        "About 6 in 10 Americans don't have moral objections to medical aid in dying": {
            "title_cn": "美国民众对安乐死道德观念调查",
            "summary_cn": "皮尤研究中心最新调查显示，约六成美国民众对医疗辅助死亡没有道德上的反对意见，认为个人应有权选择有尊严地结束生命，但党派分歧明显且深刻。共和党支持者认为医师协助死亡在道德上是错误的比例高达48%，是民主党支持者（23%）的两倍多。调查还发现，宗教信仰、年龄和教育程度对该议题态度影响显著，无宗教信仰者和年轻群体更倾向于支持安乐死合法化。该调查深刻反映了美国在生命伦理、个人自由与宗教价值观之间的社会态度分化和价值观冲突。"
        },
        "Key findings about Black immigrants in the U.S.": {
            "title_cn": "美国黑人移民群体特征研究",
            "summary_cn": "皮尤研究中心发布最新研究报告显示，美国黑人移民群体自2000年以来增长逾一倍，2024年已达到560万人，占美国黑人总人口的11.4%，成为美国黑人社区中日益重要的组成部分。报告指出，该群体主要来源于非洲和加勒比地区，教育程度和就业状况呈现多元化特征，整体教育水平高于美国本土黑人。这一人口结构变化对美国种族关系、政治格局、社会融合和文化多样性具有深远影响，也对相关政策制定和社会服务提出了新的要求和挑战。"
        },
        "Majority of Americans prefer spread-out communities with big houses": {
            "title_cn": "美国民众居住偏好调查：大房子还是便利设施",
            "summary_cn": "皮尤研究中心最新调查显示，55%的美国民众表示更愿意居住在房屋较大、空间开阔、与商业设施距离较远的社区，仅有44%的人偏好相反。报告深入分析了年龄、收入、党派归属和家庭结构等因素对居住偏好的影响，指出美国人对郊区生活方式的偏好持续存在且根深蒂固，这一趋势对城市规划和住房政策具有重要影响。调查还发现，种族和族裔背景对居住偏好也有一定影响，不同群体的居住选择反映了其生活方式和价值取向的多元化。"
        },
        "What Do Americans Consider Immoral?": {
            "title_cn": "美国人的道德观念调查",
            "summary_cn": "皮尤研究中心发布最新道德观念调查报告显示，九成美国民众认为婚外情是不道德的，但在堕胎和同性恋的道德评判上，民主党与共和党支持者存在显著且深刻的分歧，反映了价值观的极化。报告系统梳理了美国社会在婚姻、家庭、生命伦理、性行为等不同议题上的道德观念分布和演变趋势，揭示了宗教虔诚度、政治立场、教育程度和代际差异对道德判断的深刻影响。该调查对理解美国社会文化分歧、宗教与政治的互动关系以及社会价值观的变迁具有重要参考价值。"
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
    
    sources = ['brookings', 'edgov', 'whitehouse', 'ace', 'nsf_ncses', 'pewresearch']
    
    for source in sources:
        translate_source(source)
    
    print("\n" + "=" * 60)
    print("✅ 翻译流程完成")
    print(f"📊 翻译数据库统计:")
    for source in sources:
        count = len(translations_db.get(source, {}))
        print(f"   {source}: {count} 条翻译")

if __name__ == '__main__':
    main()
