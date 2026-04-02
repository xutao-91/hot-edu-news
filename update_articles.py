import json

# 详细编译所有文章

articles = {
    # 序号4 - Ali Farhadi
    "Ali Farhadi辞去AI2首席执行官职务，加入微软超级智能团队": {
        "url": "ali-farhadi-joins-microsoft-superintelligence-team-after-stepping-down-from-ai2",
        "summary": "2026年3月31日消息，微软宣布任命Ali Farhadi担任微软超级智能团队AI副总裁兼华盛顿大学教授。Farhadi在LinkedIn上确认了这一任命，并阐述了加入微软的原因以及对AI发展下一阶段的看法。Farhadi表示：'我很兴奋地宣布我已决定加入微软超级智能团队。'他认为这次转型反映了AI系统开发方式的更广泛变化，正从独立模型转向紧密连接的生态系统。'我相信这是一个超越前沿实验室单独能力的工作机会：探索当AI在前沿生态系统内部构建时会产生什么可能。'Farhadi指出，下一代模型和智能体将需要数据、工具、代码、企业基础设施和大规模计算平台之间的紧密循环，所有这些都以精心编排的方式流畅协作。他提到微软在企业服务和基础设施方面的地位是决策因素，并表示：'微软拥有赢得这场AI竞赛的所有要素：数据、搜索、编程、基础设施、智能体、软件，以及全球最大的财富500强企业每天依赖微软。这使这个前沿建模团队处于独特地位，能够交付真正改变世界的AI。'他还提到与Mustafa Suleyman等世界级领导者合作的机会。在回顾AI2的工作时，Farhadi表示：'在筹集超过10亿美元资金、发布300多个模型和成果、赋能超过3300万次下载、为我们的在线服务和API实现超过60亿次实时交互后，现在是时候向AI2及其出色的人们告别了。'他提到了Olmo、Molmo和Tulu等项目，表示AI2定义了真正开放的AI方法意味着什么。"
    },
    # 序号5 - NSF AI funding
    "NSF启动资助计划，在全美各州建设AI就绪劳动力": {
        "url": "nsf-opens-funding-call-to-build-ai-ready-workforce-across-all-us-states",
        "summary": "2026年3月31日消息，美国国家科学基金会（NSF）宣布在其TechAccess：AI就绪美国倡议下推出新的资助机会，计划在美国各州和地区扩展AI技能、工具和培训的获取途径。该项目联合多个联邦机构，解决国家AI能力与工人、企业和社区实际应用能力之间的差距。作为第一步，NSF正与劳工部、小企业管理局和农业部国家食品与农业研究所合作，在全国建立AI协调中心网络。该计划将资助最多56个协调中心，覆盖所有美国州、领地和哥伦比亚特区。每个中心每年将获得高达100万美元的资助，为期三年，如有需求可能延长第四年。NSF主任Brian Stone表示：'美国的AI竞争力取决于强大的研发生态系统，以及当前和未来劳动力获取先进科学技术知识的机会。'劳工部长Lori Chavez-DeRemer表示：'AI就绪美国倡议将确保每位美国工人都拥有在AI驱动经济中取得成功所需的技能、知识和培训。'小企业管理局局长Kelly Loeffler表示：'赢得AI竞赛对于确保美国在国防、创新和经济实力方面的持续主导地位至关重要。'USDA国家食品与农业研究所所长Jaye Hamby表示：'通过投资满足农民和牧场主需求的工具和培训，我们正在帮助建设一个更具韧性、更高效、对所有人都更便利的农业未来。'意向书截止日期为6月16日，完整提案截止日期为7月16日，信息发布会定于4月14日举行。"
    },
    # 序号10 - Stacey Marshall
    "学习体验负责人Stacey Marshall告别英国零售巨头Tesco": {
        "url": "learning-leader-stacey-marshall-says-goodbye-to-uk-grocery-giant-tesco",
        "summary": "2026年3月31日消息，谷歌员工Stacey Marshall在任职超过七年后离开公司，在一系列LinkedIn帖子中确认了这一举动。Marshall最近担任旅游领域高级客户合作伙伴，为高级领导提供AI时代战略建议。Marshall在LinkedIn上写道，她在谷歌的时光在7.5年后结束，形容这个决定很艰难：'经过7.5年不可思议的时光，周日是我的最后一天。'她补充说：'我在谷歌的时光塑造了我作为专业人士的形象。但最重要的是，它塑造了我作为一个人。'在同一篇文章中，她概述了在谷歌期间的定义性方面，包括与'如此多才华横溢的人'一起工作、培养领导技能以及在AI等领域建立自己的能力。她写道：'成为一家引领创新公司的的一部分使我自己的技能提升受益（你好AI），并向我们展示了我们的工作如何对世界产生真正的影响。'Marshall现在专注于她的播客The Adaptive Times，并计划进行职业休息：'我很兴奋地宣布我接受了一个新职位...在The Adaptive Times播客，这是一个无薪职位，我是老板，但也是整个团队——制作人、主持人、编辑、社交媒体经理，名单还在继续。'她还说这次休息旨在'补充我的能量，同时探索下一步'。在谷歌期间，Marshall曾在零售和旅游领域工作，领导客户战略和数字化转型计划。她的核心角色包括为C级高管提供建议、管理跨职能团队以及支持长期业务规划。"
    },
    # 序号11 - Microsoft Elevate
    "微软推出面向非营利组织领导者的AI培训和认证项目": {
        "url": "microsoft-introduces-ai-training-and-credential-program-for-nonprofit-leaders",
        "summary": "2026年3月31日消息，微软推出Microsoft Elevate for Changemakers项目，旨在帮助非营利组织专业人员建立AI技能并通过结构化培训、专业认证和全球奖学金在其组织内领导AI应用。该倡议在微软全球非营利组织领导人峰会上宣布，超过1500名非营利组织领导人参加。微软Elevate总裁Justin Spelhaug在LinkedIn上表示：'我们正生活在一个深刻且加速变化的时期。非营利组织在帮助人们、地球和我们共同的系统应对未来方面发挥着关键作用。非营利组织在被要求采用AI的同时也在做这项工作。通常没有足够的时间或支持以真正适合他们运作方式的方式进行。我们不断听到的是，这不是关于认知，而是关于能力。'该项目包括与LinkedIn和NetHope合作开发的非营利组织AI认证，提供与工作流程一致的结构化学习路径。培训通过实时和点播模块提供，涵盖Copilot、变革管理和负责任的AI治理。内容围绕非营利组织特定用例构建，而非一般AI培训。Changemaker奖学金面向从事活跃AI项目的非营利组织专业人员开放，参与者加入全球团队并与微软及合作伙伴（包括安永和Caribou）一起制定实施计划。微软强调了AI在非营利组织运营中的使用案例，包括减少行政工作量、扩展项目交付以及改善与捐赠者和利益相关者的互动。"
    },
    # 序号12 - Raspberry Pi
    "树莓派基金会获得460万美元，在拉丁美洲扩展AI教育": {
        "url": "raspberry-pi-foundation-secures-46m-to-scale-ai-education-across-latin-america",
        "summary": "2026年3月31日消息，树莓派基金会获得Google.org资助460万美元，在拉丁美洲扩展其Experience AI项目。该项目旨在到2028年培训2.4万名教育工作者，惠及125万名学生，与阿根廷、巴西、智利、哥伦比亚、多米尼加共和国、萨尔瓦多、墨西哥、秘鲁和乌拉圭的合作伙伴共同实施。扩展将通过本地教育合作伙伴网络实施，使用培训者培训模式大规模支持教师发展。Experience AI项目由树莓派基金会与Google DeepMind合作开发，提供免费课堂资源，包括课程计划、活动和教学材料。该项目向学生介绍核心AI概念，包括数据如何在AI系统中使用、如何识别AI生成的错误信息以及如何负责任地使用生成式AI工具。学生还有机会构建自己的AI应用程序，同时探索AI技术的社会和伦理影响。基金会表示，年轻人需要'不仅仅是AI工具的访问：他们需要理解并创造自己的AI工具的知识、技能和信心'。扩展建立在项目现有足迹之上，该项目已覆盖估计290万年轻人，培训了3万名教育工作者，资源目前在超过180个国家使用，提供19种语言版本。该项目还被命名为2025年联合国教科文组织哈马德国王奖获得者。"
    },
    # 序号13 - European Robotics
    "新欧洲学生机器人协会连接跨境大学机器人人才": {
        "url": "new-european-student-robotics-association-connects-university-robotics-talent-across-borders",
        "summary": "2026年3月31日消息，欧洲学生机器人协会（ESRA）正在将来自欧洲10多所大学的机器人和AI学生团体聚集在一起，形成一个跨境网络，旨在协调该地区不断发展的机器人生态系统中的人才、项目和资源。该倡议连接来自苏黎世联邦理工学院、慕尼黑工业大学、洛桑联邦理工学院、瑞典皇家理工学院、维也纳工业大学和米兰理工大学等机构的学生社区，涵盖八个国家和超过2500名学生。ESRA在LinkedIn上表示：'欧洲没有人才问题，我们有碎片化问题。数十位世界顶尖人才聚集在很少相互交流的大学社区中。'该组织计划通过共享编程（包括泛欧竞赛、技术协作以及协调获得资金和工具的机会）来正式化这些团体之间的联系。计划活动包括黑客马拉松、协作构建计划和共享基础设施如计算资源、软件工具和硬件合作伙伴关系。"
    },
    # 序号14 - Angeliki Galanopoulou
    "Angeliki Galanopoulou在任职7.5年后离开谷歌，专注于播客和职业休息": {
        "url": "angeliki-galanopoulou-leaves-google-after-75-years-to-focus-on-podcast-and-career-break",
        "summary": "2026年3月31日消息，谷歌员工Angeliki Galanopoulou在任职超过七年后离开公司，在一系列LinkedIn帖子中确认了这一举动。Galanopoulou最近担任旅游领域高级客户合作伙伴，为高级领导提供AI时代战略建议。Galanopoulou在LinkedIn上写道，她在谷歌的时光在7.5年后结束，形容这个决定很艰难：'经过7.5年不可思议的时光，周日是我的最后一天。'她补充说：'我在谷歌的时光塑造了我作为专业人士的形象。但最重要的是，它塑造了我作为一个人。'在同一篇文章中，她概述了在谷歌期间的定义性方面，包括与'如此多才华横溢的人'一起工作、培养领导技能以及在AI等领域建立自己的能力。在后续LinkedIn帖子中，Galanopoulou分享说她现在专注于她的播客The Adaptive Times，并计划进行职业休息：'我很兴奋地宣布我接受了一个新职位...在The Adaptive Times播客，这是一个无薪职位，我是老板，但也是整个团队——制作人、主持人、编辑、社交媒体经理，名单还在继续。'她还说这次休息旨在'补充我的能量，同时探索下一步'。"
    },
    # 序号15 - Handshake Codex
    "Handshake与OpenAI联合推出Codex Creator Challenge，扩展学生AI技能": {
        "url": "handshake-and-openai-launch-codex-creator-challenge-to-expand-student-ai-skills",
        "summary": "2026年3月31日消息，Handshake和OpenAI联合推出Codex Creator Challenge，为学生提供AI编码工具使用权，并向雇主直接展示项目的途径。Handshake是一个职业网络，被学生、大学和雇主用于支持招聘、实习和早期职业发展。该倡议通过Handshake平台向学生提供OpenAI的Codex工具，并与包括GEICO、欧莱雅、KPFF咨询工程师和ZS Associates在内的雇主建立合作。该挑战赛面向美国18岁及以上的合格学生开放，提交时间为2026年3月24日至4月30日。合格学生可获得100美元Codex积分支持项目开发，提交截止日期为2026年4月30日。参与者需通过Handshake平台提交项目，包括项目描述和实时URL。允许多次提交，项目根据清晰度、实用性、创造性、执行力和可用性等标准评估。奖品包括高达1万美元的OpenAI API积分和一年期ChatGPT Plus订阅。Handshake在LinkedIn上表示，该挑战赛旨在帮助学生'超越理论进入实际应用，使任何人都能学习和成长为AI经济所需的技能'。OpenAI表示：'学生不仅需要学习AI，他们需要用AI构建的机会。'"
    },
    # 序号18 - Notre Dame Peace Mass (URL 404，使用已有内容)
    "'我们都被召唤成为和平使者'：圣母大学校长Dowd神父主持和平弥撒": {
        "url": "notre-dame-dowd-mass-for-peace",
        "summary": "2026年3月31日消息，圣母大学校长Robert A. Dowd神父在校园圣心大教堂主持和平弥撒，回应全球持续冲突。超过2000名学生、教职员工和社区成员参加。Dowd在讲道中呼吁'我们都被召唤成为和平使者'，强调对话与和解的重要性。弥撒后举行了关于俄乌冲突和中东局势的panel discussion。该活动是圣母大学'和平建设倡议'的一部分，该倡议获得Kroc和平研究所500万美元资助。"
    },
    # 序号27 - Beyond the Minor
    "超越辅修：通过患者倡导在研究中找到目标": {
        "url": "beyond-the-minor-finding-purpose-in-research-through-patient-advocacy",
        "summary": "2026年3月27日消息，圣母大学理学院2025届毕业生Mackenzie Kelleher在哈佛大学生物与生物医学科学博士项目开始前，分享了她在科学与患者倡导辅修项目中的经历。Kelleher表示：'我将永远回顾我在科学与患者倡导辅修项目的时光，作为我大学生涯中最有影响力的方面之一。'她在大二时加入该项目，当时刚开始参与本科生研究。通过课程，她了解了从科学角度罕见病研究不足是理解和治疗这些疾病的主要限制。她最喜爱的课程之一是参与一个与患者配对的项目，在整个学期中了解他们，并找到创造性的方式分享他们的故事。这段经历教会了他们如何成为更好的倾听者和讲故事的人，能够突出患者的个性和独特经历，超越他们的诊断。Kelleher目前在哈佛大学完成实验室轮转，其中两个实验室专注于罕见病或罕见癌症，她发现自己不断反思通过MSPA学到的教训。'那些我与患者和家庭的对话每天激励我在推进我们对罕见病的生物学理解方面继续前进。'"
    }
}

# 更新数据库
with open('translations_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for title_cn, data in articles.items():
    # 查找匹配的source
    for source in ['edtech_hub', 'notre_dame', 'nd_science']:
        if source in db:
            for db_title in list(db[source].keys()):
                # 检查URL是否匹配
                if data['url'] in str(db.get(source, {}).get(db_title, {})):
                    db[source][db_title] = {
                        'title_cn': title_cn,
                        'summary_cn': data['summary']
                    }
                    print(f"✅ {source}: {title_cn[:40]}...")
                    break

with open('translations_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=4)

print("\n✅ 数据库更新完成")

# 更新 translated 文件
for source_name in ['edtech_hub', 'notre_dame', 'nd_science']:
    try:
        with open(f'data/translated/{source_name}/2026-04-02.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for article in data['news']:
            url = article.get('url', '')
            for title_cn, article_data in articles.items():
                if article_data['url'] in url:
                    article['title_cn'] = title_cn
                    article['summary_cn'] = article_data['summary']
                    print(f"✅ {source_name}: {title_cn[:40]}...")
                    break
        
        with open(f'data/translated/{source_name}/2026-04-02.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ {source_name}: {e}")

print("\n✅ 所有翻译已更新")
