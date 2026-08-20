// 专有名词 / 术语表数据
// 结构: [w 英文, c 中文, s 例句, cat 分类, ipa 音标(可选)]
// 分类: 身体词 / 海洋 / 海峡 / 海湾 / 大陆 / 海洋生物 / 叙述方式 / 灭绝事件 / 地质年代 / 写景词
const PROPER_NOUNS = [
  // ===== 日常词（日耳曼语源）vs 学术词（拉丁语源）=====
  ["nose", "鼻子（日常词；学术词 nasal）", "The whale breathes through a blowhole on top of its head rather than through its nose.", "身体词", "/noʊz/"],
  ["nasal", "鼻的（学术词；日常词 nose）", "The nasal cavity warms and moistens the air we breathe.", "身体词", "/ˈneɪ.zəl/"],
  ["nasal sacs", "鼻囊：既可指人的鼻腔，也可指海豚的鼻腔（后者的结构更复杂）", "The nasal sacs of dolphins are far more complex than those of humans.", "身体词", ""],
  ["mouth", "口，嘴（日常词；学术词 oral）；河口", "The river enters the sea at its mouth, where fresh water meets salt water.", "身体词", "/maʊθ/"],
  ["oral", "口的（学术词；日常词 mouth）", "The oral cavity is the first part of the digestive tract.", "身体词", "/ˈɔːr.əl/"],
  ["ear", "耳朵（日常词；学术词 aural / otic）", "Bats use their large ears to navigate in the dark.", "身体词", "/ɪr/"],
  ["aural", "耳的，听觉的（学术词；日常词 ear）", "The aural test requires students to identify words they hear.", "身体词", "/ˈɔːr.əl/"],
  ["otic", "耳的（更专业的医学用词）", "The otic region of the skull houses the organs of hearing.", "身体词", "/ˈoʊ.tɪk/"],
  ["tooth", "牙齿（日常词；学术词 dental）", "The fossilized tooth of a mammoth was discovered near the glacier.", "身体词", "/tuːθ/"],
  ["dental", "牙齿的（学术词；日常词 tooth）", "Dental enamel is the hardest substance in the human body.", "身体词", "/ˈden.t̬əl/"],
  ["heart", "心脏（日常词；学术词 cardiac）", "The heart pumps blood through the entire circulatory system.", "身体词", "/hɑːrt/"],
  ["cardiac", "心脏的（学术词；日常词 heart）", "Cardiac muscle contracts rhythmically without conscious effort.", "身体词", "/ˈkɑːr.di.æk/"],
  ["lung", "肺（日常词；学术词 pulmonary）", "The smog damaged the lungs of residents living near the factory.", "身体词", "/lʌŋ/"],
  ["pulmonary", "肺的（学术词；日常词 lung）", "Pulmonary arteries carry blood from the heart to the lungs.", "身体词", "/ˈpʊl.mə.ner.i/"],
  ["liver", "肝脏（日常词；学术词 hepatic）", "The liver filters toxins out of the blood.", "身体词", "/ˈlɪv.ər/"],
  ["hepatic", "肝脏的（学术词；日常词 liver）", "Hepatic cells process nutrients absorbed from the intestine.", "身体词", "/hɪˈpæt̬.ɪk/"],

  // ===== 五大洋 =====
  ["Pacific Ocean", "太平洋（世界上面积最大、最深的大洋）", "The Pacific Ocean is the largest and deepest ocean on Earth.", "海洋", "/pəˈsɪf.ɪk ˈoʊ.ʃən/"],
  ["Atlantic Ocean", "大西洋（世界第二大洋，形状呈 S 形）", "The Atlantic Ocean is shaped roughly like the letter S.", "海洋", "/ətˈlæn.tɪk ˈoʊ.ʃən/"],
  ["Indian Ocean", "印度洋（世界第三大洋，大部分位于南半球）", "The Indian Ocean lies mostly in the Southern Hemisphere.", "海洋", "/ˈɪn.di.ən ˈoʊ.ʃən/"],
  ["Arctic Ocean", "北冰洋（面积最小、最浅的大洋，位于北极地区）", "The Arctic Ocean is the smallest and shallowest of the five oceans.", "海洋", "/ˈɑːrk.tɪk ˈoʊ.ʃən/"],
  ["Southern Ocean", "南大洋（2000 年划定的新大洋，环绕南极洲）", "The Southern Ocean surrounds the continent of Antarctica.", "海洋", "/ˈsʌð.ərn ˈoʊ.ʃən/"],

  // ===== 重要海域 =====
  ["Mediterranean Sea", "地中海（位于欧、亚、非三洲之间）", "The Mediterranean Sea lies between Europe, Asia, and Africa.", "海洋", "/ˌmed.ɪ.təˈreɪ.ni.ən ˈsiː/"],
  ["Red Sea", "红海（位于非洲和阿拉伯半岛之间）", "The Red Sea separates Africa from the Arabian Peninsula.", "海洋", "/red siː/"],
  ["Black Sea", "黑海（位于欧洲和亚洲之间）", "The Black Sea lies between Europe and Asia.", "海洋", "/blæk siː/"],
  ["Caspian Sea", "里海（世界上最大的内陆湖，常被称为“海”）", "The Caspian Sea is the largest inland lake in the world.", "海洋", "/ˈkæs.pi.ən ˈsiː/"],
  ["Baltic Sea", "波罗的海（位于北欧）", "The Baltic Sea is located in northern Europe.", "海洋", "/ˈbɔːl.tɪk ˈsiː/"],
  ["North Sea", "北海（位于大西洋东北部，欧洲西北岸）", "The North Sea lies in the northeastern Atlantic, off the coast of northwestern Europe.", "海洋", "/nɔːrθ siː/"],
  ["Caribbean Sea", "加勒比海（位于大西洋西部，美洲中部）", "The Caribbean Sea is home to thousands of islands.", "海洋", "/ˌkær.ɪˈbiː.ən ˈsiː/"],
  ["Arabian Sea", "阿拉伯海（位于印度洋西北部）", "The Arabian Sea lies in the northwestern part of the Indian Ocean.", "海洋", "/əˈreɪ.bi.ən ˈsiː/"],
  ["South China Sea", "南中国海（位于太平洋西部）", "The South China Sea is an important shipping route in the western Pacific.", "海洋", "/saʊθ ˈtʃaɪ.nə siː/"],

  // ===== 重要海峡 =====
  ["Strait of Gibraltar", "直布罗陀海峡（连接地中海与大西洋）", "The Strait of Gibraltar connects the Mediterranean Sea with the Atlantic Ocean.", "海峡", "/streɪt əv dʒɪˈbrɔːl.tər/"],
  ["Strait of Malacca", "马六甲海峡（连接印度洋与太平洋 / 南海）", "The Strait of Malacca links the Indian Ocean with the Pacific Ocean.", "海峡", "/streɪt əv məˈlæk.ə/"],
  ["English Channel", "英吉利海峡（连接大西洋与北海）", "The English Channel separates England from France.", "海峡", "/ˈɪŋ.ɡlɪʃ ˈtʃæn.əl/"],
  ["Bering Strait", "白令海峡（连接北冰洋与太平洋）", "The Bering Strait connects the Arctic Ocean with the Pacific Ocean.", "海峡", "/ˈber.ɪŋ streɪt/"],
  ["Strait of Hormuz", "霍尔木兹海峡（连接波斯湾与印度洋）", "The Strait of Hormuz connects the Persian Gulf with the Indian Ocean.", "海峡", "/streɪt əv hɔːrˈmuːz/"],

  // ===== 重要海湾 =====
  ["Gulf of Mexico", "墨西哥湾（位于北美洲东南部）", "The Gulf of Mexico lies off the southeastern coast of North America.", "海湾", "/ɡʌlf əv ˈmek.sɪ.koʊ/"],
  ["Persian Gulf", "波斯湾（位于西亚，石油资源丰富）", "The Persian Gulf is rich in petroleum resources.", "海湾", "/ˈpɜːr.ʒən ɡʌlf/"],
  ["Gulf of Guinea", "几内亚湾（位于西非）", "The Gulf of Guinea is located off the coast of West Africa.", "海湾", "/ɡʌlf əv ˈɡɪn.i/"],
  ["Gulf of Alaska", "阿拉斯加湾（位于北美洲西北部）", "The Gulf of Alaska lies in the northwestern part of North America.", "海湾", "/ɡʌlf əv əˈlæs.kə/"],
  ["Bay of Bengal", "孟加拉湾（世界上最大的海湾）", "The Bay of Bengal is the largest bay in the world.", "海湾", "/beɪ əv beŋˈɡɔːl/"],

  // ===== 大陆 =====
  ["Antarctica", "南极洲", "Antarctica is the coldest and driest continent on Earth.", "大陆", "/ænˈtɑːrk.tɪ.kə/"],
  ["Oceania", "大洋洲", "Oceania includes Australia, New Zealand, and thousands of Pacific islands.", "大陆", "/ˌoʊ.ʃiˈæn.i.ə/"],

  // ===== 海洋生物 =====
  ["microscopic marine plants", "微型海洋植物（浮游植物，海洋食物链的基础）", "Microscopic marine plants produce nearly half of the oxygen in the atmosphere.", "海洋生物", "/ˌmaɪ.krəˈskɑː.pɪk məˈriːn plænts/"],
  ["microorganisms", "微生物", "Microorganisms in the ocean decompose dead organic matter and recycle nutrients.", "海洋生物", "/ˌmaɪ.kroʊˈɔːr.ɡə.nɪz.əmz/"],

  // ===== 叙述方式 =====
  ["chronological order", "顺叙（事件按实际发生顺序讲述：1→2→3→4）", "The professor asked us to arrange the events in chronological order.", "叙述方式", "/ˌkrɒn.əˈlɒdʒ.ɪ.kəl ˈɔːr.dər/"],
  ["flashback", "倒叙（从中间或结局开始，再回头讲之前的事：3→1→2→4）", "The story begins with a flashback to the main character's childhood.", "叙述方式", "/ˈflæʃ.bæk/"],
  ["in medias res", "插叙 / 从故事中途开始（非线性的叙述方式）", "Many epic poems begin in medias res, dropping the reader into the middle of the action.", "叙述方式", "/ɪn ˌmeɪ.di.æs ˈreɪs/"],
  ["non-linear", "非线性的（中间穿插过去和未来的叙述方式）", "The film uses a non-linear narrative that jumps between past and present.", "叙述方式", "/nɑːn ˈlɪn.i.ər/"],

  // ===== 灭绝事件 =====
  ["Ordovician-Silurian extinction", "奥陶纪-志留纪灭绝事件", "The Ordovician-Silurian extinction wiped out most marine species about 443 million years ago.", "灭绝事件", "/ˌɔːr.dəˈvɪʃ.ən sɪˈlʊr.i.ən ɪkˈstɪŋk.ʃən/"],
  ["Late Devonian extinction", "晚泥盆世灭绝事件", "The Late Devonian extinction mainly affected marine organisms such as reef-building corals.", "灭绝事件", "/leɪt dɪˈvoʊ.ni.ən ɪkˈstɪŋk.ʃən/"],
  ["Permian-Triassic extinction", "二叠纪-三叠纪灭绝事件（也称“大死亡” The Great Dying）", "The Permian-Triassic extinction, also called the Great Dying, was the most severe extinction event in Earth's history.", "灭绝事件", "/ˈpɜːr.mi.ən traɪˈæs.ɪk ɪkˈstɪŋk.ʃən/"],
  ["The Great Dying", "“大死亡”（二叠纪-三叠纪灭绝事件的别称）", "The Great Dying is another name for the Permian-Triassic extinction.", "灭绝事件", "/ðə ɡreɪt ˈdaɪ.ɪŋ/"],
  ["Triassic-Jurassic extinction", "三叠纪-侏罗纪灭绝事件", "The Triassic-Jurassic extinction cleared the way for dinosaurs to dominate the land.", "灭绝事件", "/traɪˈæs.ɪk dʒʊˈræs.ɪk ɪkˈstɪŋk.ʃən/"],
  ["Cretaceous-Paleogene extinction", "白垩纪-古近纪灭绝事件（恐龙灭绝的那次，简称 K-Pg）", "The Cretaceous-Paleogene extinction event is famous for wiping out the dinosaurs.", "灭绝事件", "/krɪˈteɪ.ʃəs ˈpæl.i.ə.dʒiːn ɪkˈstɪŋk.ʃən/"],

  // ===== 地质年代 =====
  ["Ordovician", "奥陶纪", "Trilobites were abundant in the oceans during the Ordovician period.", "地质年代", "/ˌɔːr.dəˈvɪʃ.ən/"],
  ["Devonian", "泥盆纪", "Fish diversified rapidly during the Devonian period.", "地质年代", "/dɪˈvoʊ.ni.ən/"],
  ["Permian", "二叠纪", "The Permian period ended with the largest mass extinction in Earth's history.", "地质年代", "/ˈpɜːr.mi.ən/"],
  ["Triassic", "三叠纪", "Dinosaurs first appeared during the Triassic period.", "地质年代", "/traɪˈæs.ɪk/"],
  ["Cretaceous", "白垩纪", "Flowering plants spread widely during the Cretaceous period.", "地质年代", "/krɪˈteɪ.ʃəs/"],

  // ===== 写景词（例句来源：一段晨光描写）=====
  ["morning light", "晨光（下面例句出自一段山巅写景）", "Morning light spreads gently across an open mountain top, touching the stone marker, the low shrubs growing over rocky ground, the far ridges beyond, and a small stacked cairn.", "写景词", ""],
  ["cairn", "石堆，石冢（用于标记路径或山顶）", "A small stacked cairn marked the summit of the mountain.", "写景词", "/kern/"],
  ["ridge", "山脊，山岭", "The hikers followed the ridge to reach the summit.", "写景词", "/rɪdʒ/"],
  ["shrub", "灌木", "Low shrubs grow over the rocky ground on the mountain top.", "写景词", "/ʃrʌb/"],
];
