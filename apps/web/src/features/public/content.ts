export const landingPainPoints = [
  { emoji: '😩', title: '每次从零写教案', description: '一份完整教案经常要耗掉两个小时。' },
  { emoji: '😩', title: '网上抄来的教案', description: '结构混乱、内容不贴班级情况，改起来更累。' },
  { emoji: '😩', title: '改完的 Word 文档', description: '下次想复用时又找不到，经验沉淀不下来。' },
];

export const landingFeatures = [
  {
    id: 'features',
    index: '①',
    title: '选学科和主题',
    description: '3 步选择，10 秒完成。',
    bullets: ['学科卡片选择', '年级卡片选择', '输入课题与补充说明'],
  },
  {
    id: 'generate',
    index: '②',
    title: 'AI 生成结构化教案',
    description: '教学目标、重难点、教学过程，一键生成。',
    bullets: ['固定骨架先出现', '逐段补充内容', '待确认内容内联展示'],
  },
  {
    id: 'edit',
    index: '③',
    title: '在线编辑，随时调整',
    description: '不满意？选中任意段落，AI 帮你重写。',
    bullets: ['像文档一样直接编辑', '局部 AI 润色与扩写', '历史版本可恢复'],
  },
  {
    id: 'export',
    index: '④',
    title: '导出 Word，直接用',
    description: '排版整洁，导出后就能打印或继续发给同事。',
    bullets: ['Word/PDF 导出', '预览导出效果', '仅导出已确认内容'],
  },
];

export const landingPersonas = [
  {
    emoji: '🎓',
    title: '新手教师',
    problem: '刚入职，不知道一份教案怎么写才专业。',
    value: 'AI 先给你完整结构和内容，再按自己的风格修改。',
  },
  {
    emoji: '📚',
    title: '教培老师',
    problem: '每天备 3 到 5 节课，时间根本不够。',
    value: '10 分钟搞定一份高质量教案，把时间还给授课本身。',
  },
  {
    emoji: '🏠',
    title: '大学生家教',
    problem: '第一次带学生，不知道怎么组织讲解。',
    value: '选好主题就能拿到完整讲义和练习结构，直接上手。',
  },
];

export const pricingFaqs = [
  {
    question: '免费版有什么限制？',
    answer: '免费版提供每月 5 份教案的参考额度，并保留基础编辑与 Word 导出能力。',
  },
  {
    question: '可以随时取消订阅吗？',
    answer: '可以。Phase 3 先展示订阅方案，不会真的扣费或锁定功能。',
  },
  {
    question: '支持哪些支付方式？',
    answer: '产品规划支持微信支付和支付宝，真实支付接入放到后续阶段。',
  },
  {
    question: '学校或机构有团购优惠吗？',
    answer: '可以联系我们获取定制方案，团队版目前仍处于展示阶段。',
  },
];

export const helpGroups = [
  {
    title: '快速入门',
    items: [
      {
        question: '如何创建第一份教案？',
        answer: '登录后进入备课台，点击“开始备课”，按学科、年级、课题完成 3 步创建即可。',
      },
      {
        question: '如何编辑 AI 生成的内容？',
        answer: 'AI 生成内容会以内联待确认卡片出现，你可以接受、拒绝或重新生成后再进入正式文档。',
      },
      {
        question: '如何导出为 Word 文档？',
        answer: '在编辑器顶部点击“导出”，选择 Word 或 PDF，系统只会导出已确认内容。',
      },
      {
        question: '支持哪些学科和年级？',
        answer: '当前覆盖常见中小学学科与年级，先满足主流备课场景。',
      },
    ],
  },
  {
    title: 'AI 功能',
    items: [
      {
        question: 'AI 生成的教案质量怎么样？',
        answer: 'LessonPilot 会优先给出结构完整的草稿，但最终教学内容仍需要教师审核把关。',
      },
      {
        question: '如何让 AI 重新生成某个段落？',
        answer: '在编辑器里悬停 block 后点击“AI 重写”，或在段落中选中文本使用“AI 润色 / AI 扩写”。',
      },
      {
        question: 'AI 生成的内容会有错误吗？',
        answer: '会有概率出现事实或表达偏差，所以系统默认把 AI 生成内容标记为待确认状态。',
      },
      {
        question: '我的教案内容会被用于 AI 训练吗？',
        answer: '不会。你的教案内容不会被用于训练模型，这是我们的明确承诺。',
      },
    ],
  },
  {
    title: '账户与付费',
    items: [
      {
        question: '如何验证邮箱？',
        answer: '注册后会异步发送验证邮件，你也可以在账户设置页重新发送验证邮件。',
      },
      {
        question: '忘记密码怎么办？',
        answer: '在登录页点击“忘记密码”，输入注册邮箱后即可收到重置链接。',
      },
      {
        question: '如何升级到专业版？',
        answer: 'Phase 3 先展示专业版方案和升级入口，真实支付能力将在后续阶段接入。',
      },
      {
        question: '可以删除自己的数据吗？',
        answer: '可以。你可以在账户设置的“数据管理”中导出全部数据或永久删除账户。',
      },
    ],
  },
];

export const privacySections = [
  {
    id: 'collect',
    title: '我们收集哪些信息',
    paragraphs: [
      '当你注册 LessonPilot 时，我们会收集你的姓名、邮箱和账户密码，用来创建和保护你的账户。',
      '当你使用备课功能时，我们会保存你创建的任务、教案内容、导出记录与必要的操作日志，用于提供产品功能本身。',
    ],
  },
  {
    id: 'usage',
    title: '我们如何使用这些信息',
    paragraphs: [
      '这些信息仅用于提供 AI 备课、文档保存、导出、账户安全和必要的产品通知。',
      '我们不会把你的教案内容用于训练 AI 模型，也不会把这些内容出售给第三方。',
    ],
  },
  {
    id: 'storage',
    title: '信息存储与安全',
    paragraphs: [
      '用户数据默认存储在中国境内服务器，数据库访问受访问控制和最小权限策略保护。',
      '密码不会以明文保存，而是经过安全哈希处理后再存储。',
    ],
  },
  {
    id: 'third-party',
    title: '第三方服务说明',
    paragraphs: [
      '当你触发 AI 生成功能时，教案相关上下文会发送给配置中的第三方 AI 服务用于即时生成，不会被我们用于训练模型。',
      '你可以在账户设置中导出自己的数据，也可以永久删除账户和关联内容。',
    ],
  },
  {
    id: 'rights',
    title: '你的权利',
    paragraphs: [
      '你可以随时访问、更正、导出和删除自己的数据。',
      '如果你对隐私政策有疑问，可以通过关于我们页面中的联系方式联系我们。',
    ],
  },
];

export const termsSections = [
  {
    id: 'account',
    title: '账户责任',
    paragraphs: [
      '你需要妥善保管自己的登录凭证，并对自己账户下发生的操作负责。',
      '如果发现账户异常，请尽快修改密码并联系我们。',
    ],
  },
  {
    id: 'payment',
    title: '付费与退款说明',
    paragraphs: [
      '当前页面中的定价信息仅用于展示产品规划，不构成真实扣费行为。',
      '真实支付、订阅和退款政策会在后续付费阶段上线时单独补充说明。',
    ],
  },
  {
    id: 'ai',
    title: 'AI 内容免责声明',
    paragraphs: [
      'AI 生成内容仅供参考，教师需自行审核其准确性、适用性和最终教学效果。',
      'LessonPilot 不替代教师的专业判断，也不对未审核的 AI 内容承担教学适配责任。',
    ],
  },
  {
    id: 'copyright',
    title: '知识产权',
    paragraphs: [
      '用户创建和编辑的教案内容归用户所有，LessonPilot 仅在提供服务所必需的范围内处理这些内容。',
      '产品界面、品牌名称和相关代码资产归 LessonPilot 所有。',
    ],
  },
  {
    id: 'service',
    title: '服务中断与免责',
    paragraphs: [
      '我们会尽力保持服务可用，但仍可能因为维护、网络、第三方服务波动等原因出现短暂中断。',
      '对于超出合理控制范围的服务中断，我们会尽快修复并降低影响。',
    ],
  },
];

export const changelogEntries = [
  {
    date: '2026-04-11',
    title: 'Phase 3 开发启动',
    items: ['开始补齐公域页面、Auth 完善、设置页、反馈入口与备课台更多操作。'],
  },
  {
    date: '2026-04-11',
    title: 'Phase 2 严格返工完成',
    items: ['编辑器按设计稿重做，补齐 AI 补充内容、历史版本、导出预览和结构化交互。'],
  },
  {
    date: '2026-04-11',
    title: 'Phase 1 主链路完成',
    items: ['完成注册、创建任务、AI 生成、编辑、导出 Word 的端到端闭环。'],
  },
];
