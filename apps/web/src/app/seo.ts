import type { RouteLocationNormalizedLoaded } from 'vue-router';

export interface SeoMeta {
  title: string;
  description: string;
  canonicalPath: string;
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  robots?: string;
}

const siteName = 'LessonPilot';

const seoMap: Record<string, SeoMeta> = {
  landing: {
    title: 'LessonPilot | 10 分钟，搞定一份好教案',
    description: 'AI 赋能的结构化备课工具。3 步创建主题，逐段生成教案，在线编辑并导出 Word / PDF。',
    canonicalPath: '/',
  },
  pricing: {
    title: '定价 | LessonPilot',
    description: '查看 LessonPilot 免费版与专业版的定价、试用和手动续费方式。',
    canonicalPath: '/pricing',
  },
  help: {
    title: '帮助中心 | LessonPilot',
    description: '快速了解如何创建教案、使用 AI 功能、管理账户和付费。',
    canonicalPath: '/help',
  },
  about: {
    title: '关于我们 | LessonPilot',
    description: '了解 LessonPilot 的产品理念、服务对象和联系方式。',
    canonicalPath: '/about',
  },
  privacy: {
    title: '隐私政策 | LessonPilot',
    description: '了解 LessonPilot 如何收集、使用、存储和删除你的数据。',
    canonicalPath: '/privacy',
  },
  terms: {
    title: '服务条款 | LessonPilot',
    description: '查看 LessonPilot 的服务条款、付费说明与 AI 内容免责声明。',
    canonicalPath: '/terms',
  },
  changelog: {
    title: '更新日志 | LessonPilot',
    description: '查看 LessonPilot 最近的版本更新与能力演进。',
    canonicalPath: '/changelog',
  },
  login: {
    title: '登录 | LessonPilot',
    description: '登录 LessonPilot，继续进入备课台和编辑器。',
    canonicalPath: '/login',
    robots: 'noindex, nofollow',
  },
  register: {
    title: '注册 | LessonPilot',
    description: '注册 LessonPilot，开始体验结构化 AI 备课流程。',
    canonicalPath: '/register',
    robots: 'noindex, nofollow',
  },
  'forgot-password': {
    title: '忘记密码 | LessonPilot',
    description: '通过邮箱重置你的 LessonPilot 登录密码。',
    canonicalPath: '/forgot-password',
    robots: 'noindex, nofollow',
  },
  'reset-password': {
    title: '重置密码 | LessonPilot',
    description: '设置新的 LessonPilot 登录密码。',
    canonicalPath: '/reset-password',
    robots: 'noindex, nofollow',
  },
  'verify-email': {
    title: '验证邮箱 | LessonPilot',
    description: '完成 LessonPilot 邮箱验证，保持账户安全。',
    canonicalPath: '/verify-email',
    robots: 'noindex, nofollow',
  },
  tasks: {
    title: '备课台 | LessonPilot',
    description: '管理你的教案任务、最近备课和搜索结果。',
    canonicalPath: '/tasks',
    robots: 'noindex, nofollow',
  },
  'task-create': {
    title: '开始备课 | LessonPilot',
    description: '通过 3 步向导创建新的 LessonPilot 教案任务。',
    canonicalPath: '/tasks/new',
    robots: 'noindex, nofollow',
  },
  editor: {
    title: '编辑器 | LessonPilot',
    description: '在 LessonPilot 编辑器中继续确认、修改和导出教案。',
    canonicalPath: '/tasks/editor',
    robots: 'noindex, nofollow',
  },
  settings: {
    title: '账户设置 | LessonPilot',
    description: '管理 LessonPilot 的账户信息、订阅与数据。',
    canonicalPath: '/settings',
    robots: 'noindex, nofollow',
  },
  'admin-overview': {
    title: '管理后台 | LessonPilot',
    description: '查看 LessonPilot 的运营概览和后台指标。',
    canonicalPath: '/admin',
    robots: 'noindex, nofollow',
  },
  'admin-users': {
    title: '用户管理 | LessonPilot',
    description: '查看 LessonPilot 的用户列表与订阅状态。',
    canonicalPath: '/admin/users',
    robots: 'noindex, nofollow',
  },
  'admin-user-detail': {
    title: '用户详情 | LessonPilot',
    description: '查看 LessonPilot 用户详情、任务、反馈与额度调整。',
    canonicalPath: '/admin/users',
    robots: 'noindex, nofollow',
  },
  notFound: {
    title: '页面不存在 | LessonPilot',
    description: '你访问的页面不存在，返回首页继续了解 LessonPilot。',
    canonicalPath: '/404',
    robots: 'noindex, nofollow',
  },
};

function getBaseUrl(): string {
  return (import.meta.env.VITE_APP_BASE_URL || 'http://localhost:5173').replace(/\/$/, '');
}

export function getSeoMeta(route: RouteLocationNormalizedLoaded): SeoMeta {
  const seoKey = String(route.meta.seoKey || route.name || 'landing');
  const baseMeta = seoMap[seoKey] ?? seoMap.landing;
  const ogImage = `${getBaseUrl()}/og-default.svg`;
  return {
    ...baseMeta,
    ogTitle: baseMeta.ogTitle || baseMeta.title,
    ogDescription: baseMeta.ogDescription || baseMeta.description,
    ogImage,
    robots: baseMeta.robots || 'index, follow',
  };
}

export function renderSeoHead(route: RouteLocationNormalizedLoaded): string {
  const meta = getSeoMeta(route);
  const canonical = `${getBaseUrl()}${meta.canonicalPath}`;
  return [
    `<title>${meta.title}</title>`,
    `<meta name="description" content="${meta.description}" />`,
    `<meta name="robots" content="${meta.robots}" />`,
    `<link rel="canonical" href="${canonical}" />`,
    `<meta property="og:site_name" content="${siteName}" />`,
    `<meta property="og:type" content="website" />`,
    `<meta property="og:title" content="${meta.ogTitle}" />`,
    `<meta property="og:description" content="${meta.ogDescription}" />`,
    `<meta property="og:url" content="${canonical}" />`,
    `<meta property="og:image" content="${meta.ogImage}" />`,
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<meta name="twitter:title" content="${meta.ogTitle}" />`,
    `<meta name="twitter:description" content="${meta.ogDescription}" />`,
    `<meta name="twitter:image" content="${meta.ogImage}" />`,
  ].join('\n');
}

export function applySeo(route: RouteLocationNormalizedLoaded): void {
  if (typeof document === 'undefined') {
    return;
  }

  const meta = getSeoMeta(route);
  document.title = meta.title;

  const tags: Array<[string, string]> = [
    ['meta[name="description"]', meta.description],
    ['meta[name="robots"]', meta.robots || 'index, follow'],
    ['link[rel="canonical"]', `${getBaseUrl()}${meta.canonicalPath}`],
    ['meta[property="og:title"]', meta.ogTitle || meta.title],
    ['meta[property="og:description"]', meta.ogDescription || meta.description],
    ['meta[property="og:url"]', `${getBaseUrl()}${meta.canonicalPath}`],
    ['meta[property="og:image"]', meta.ogImage || `${getBaseUrl()}/og-default.svg`],
    ['meta[name="twitter:title"]', meta.ogTitle || meta.title],
    ['meta[name="twitter:description"]', meta.ogDescription || meta.description],
    ['meta[name="twitter:image"]', meta.ogImage || `${getBaseUrl()}/og-default.svg`],
  ];

  for (const [selector, value] of tags) {
    const element = document.querySelector(selector);
    if (!element) {
      continue;
    }
    if (element instanceof HTMLLinkElement) {
      element.href = value;
    } else {
      element.setAttribute('content', value);
    }
  }
}
