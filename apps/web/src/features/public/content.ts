export const landingPainPoints = [
  { icon: 'clock', title: '明天要交，今晚才开始', description: '最焦虑的不是写不出来，而是不知道这份能不能交。' },
  { icon: 'files', title: '旧资料散在各处', description: 'Word、PPT、讲义都能用，但每次复用都要重新翻。' },
  { icon: 'folder', title: '学校格式总要返工', description: '内容写完还要套表格、补栏目、检查反思和签字区。' },
];

export const landingFeatures = [
  {
    id: 'features',
    index: '①',
    title: '课题和旧资料一起进来',
    description: '新备课可以从课题开始，也可以从旧 Word 教案开始。',
    bullets: ['输入课题快速起草', '导入旧教案预览结构', '推荐个人资料库内容'],
  },
  {
    id: 'generate',
    index: '②',
    title: '先整理出完整初稿',
    description: '教学目标、重难点和流程会按 section 写进文档。',
    bullets: ['纸张画布直接阅读', '按章节补齐正文', '待确认内容清楚标记'],
  },
  {
    id: 'edit',
    index: '③',
    title: '质量、引用、资料在右侧',
    description: '不用在多个页面之间跳，导出风险和参考资料都在文档旁边。',
    bullets: ['导出前体检', '知识库和我的资料引用', '学校模板随时切换'],
  },
  {
    id: 'export',
    index: '④',
    title: '导出学校格式 Word',
    description: '确认过的内容进入 Word，未确认内容不会悄悄混进去。',
    bullets: ['模板化 Word 导出', '预览导出效果', '仅导出已确认内容'],
  },
];

export const landingPersonas = [
  {
    icon: 'graduate',
    title: '新手教师',
    problem: '刚入职，不知道一份教案怎么写才专业。',
    value: '先拿到完整结构和初稿，再按自己的班级情况细调。',
  },
  {
    icon: 'book',
    title: '教培老师',
    problem: '每天备 3 到 5 节课，时间根本不够。',
    value: '先拿到可修改初稿，再让质量体检帮你找提交风险。',
  },
  {
    icon: 'home',
    title: '大学生家教',
    problem: '第一次带学生，不知道怎么组织讲解。',
    value: '选好主题就能拿到教案、学案或讲义结构，直接上手。',
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
        question: '如何编辑系统整理出的内容？',
        answer: '系统整理出的内容会以内联待确认卡片出现，你可以保留、丢弃，或再次整理后再并入正式文档。',
      },
      {
        question: '如何导出 Word 文档？',
        answer: '在编辑器顶部点击“导出 Word”，系统会把已确认内容整理成 Word 文档。',
      },
      {
        question: '支持哪些学科和年级？',
        answer: '当前优先围绕语文备课场景打磨，后续是否扩展会以实际使用反馈为准。',
      },
    ],
  },
  {
    title: '起草与编辑',
    items: [
      {
        question: '教案初稿质量怎么样？',
        answer: 'LessonPilot 会优先给出结构完整、便于继续修改的初稿，但最终教学内容仍需要教师审核把关。',
      },
      {
        question: '如何重新处理某个段落？',
        answer: '在编辑器里悬停段落后点击“改写”，或在段落中选中文本使用“补充展开 / 压缩表达”。',
      },
      {
        question: '起草的内容会有错误吗？',
        answer: '会有概率出现事实或表达偏差，所以系统默认把整理出的内容标记为待确认状态。',
      },
      {
        question: '我的教案内容会被用于模型训练吗？',
        answer: '不会。你的教案内容不会被用于训练模型，这是我们的明确承诺。',
      },
    ],
  },
  {
    title: '账户与数据',
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
      '这些信息仅用于提供备课服务、文档保存、导出、账户安全和必要的产品通知。',
      '我们不会把你的教案内容用于训练模型，也不会把这些内容出售给第三方。',
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
      '当你触发内容起草或段落整理时，教案相关上下文会发送给配置中的第三方服务完成即时处理，不会被我们用于训练模型。',
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
    id: 'service-nature',
    title: '服务性质说明',
    paragraphs: [
      '当前阶段 LessonPilot 仅作为个人备课工具体验，重点验证备课、编辑、导入、检查和 Word 导出流程。',
      '功能范围可能会随备案、测试和实际使用反馈调整，页面展示不构成任何服务可用性承诺。',
    ],
  },
  {
    id: 'ai',
    title: '内容免责声明',
    paragraphs: [
      '系统整理出的内容仅供参考，教师需自行审核其准确性、适用性和最终教学效果。',
      'LessonPilot 不替代教师的专业判断，也不对未审核的起草内容承担教学适配责任。',
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
    items: ['编辑器按设计稿重做，补齐补充内容、历史版本、导出预览和结构化交互。'],
  },
  {
    date: '2026-04-11',
    title: 'Phase 1 主链路完成',
    items: ['完成注册、创建任务、内容起草、编辑、导出 Word 的端到端闭环。'],
  },
];
