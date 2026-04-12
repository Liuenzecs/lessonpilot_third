/* global console, process */

import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import compression from 'compression';
import express from 'express';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const resolve = (...parts) => path.resolve(__dirname, ...parts);

const app = express();
const isProd = process.env.NODE_ENV === 'production';
const port = Number(process.env.PORT || 5173);
const appBaseUrl = (process.env.APP_BASE_URL || process.env.VITE_APP_BASE_URL || `http://localhost:${port}`).replace(/\/$/, '');
const publicSsrPaths = new Set(['/', '/pricing', '/help', '/about', '/privacy', '/terms', '/changelog', '/500', '/network-error']);
const privatePrefixes = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email', '/tasks', '/settings', '/admin'];

function shouldSsr(pathname) {
  if (pathname === '/robots.txt' || pathname === '/sitemap.xml') {
    return false;
  }
  if (privatePrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`))) {
    return false;
  }
  if (/\.[a-z0-9]+$/i.test(pathname)) {
    return false;
  }
  return publicSsrPaths.has(pathname) || !pathname.startsWith('/api/');
}

function renderSitemap() {
  const paths = ['/', '/pricing', '/help', '/about', '/privacy', '/terms', '/changelog'];
  const urls = paths
    .map(
      (pathname) => `
  <url>
    <loc>${appBaseUrl}${pathname}</loc>
  </url>`,
    )
    .join('');
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}
</urlset>`;
}

function defaultHead() {
  return [
    '<title>LessonPilot</title>',
    '<meta name="description" content="LessonPilot 是 AI 赋能的结构化备课工具，帮助老师 10 分钟完成一份高质量教案。" />',
    '<meta name="robots" content="noindex, nofollow" />',
    `<link rel="canonical" href="${appBaseUrl}/" />`,
    '<meta property="og:site_name" content="LessonPilot" />',
    '<meta property="og:type" content="website" />',
    '<meta property="og:title" content="LessonPilot" />',
    '<meta property="og:description" content="AI 赋能的结构化备课工具，帮助老师快速生成、编辑和导出教案。" />',
    `<meta property="og:image" content="${appBaseUrl}/og-default.svg" />`,
    `<meta property="og:url" content="${appBaseUrl}/" />`,
    '<meta name="twitter:card" content="summary_large_image" />',
    '<meta name="twitter:title" content="LessonPilot" />',
    '<meta name="twitter:description" content="AI 赋能的结构化备课工具，帮助老师快速生成、编辑和导出教案。" />',
    `<meta name="twitter:image" content="${appBaseUrl}/og-default.svg" />`,
  ].join('\n');
}

async function createNodeSentry() {
  const dsn = process.env.SENTRY_DSN_WEB || process.env.VITE_SENTRY_DSN_WEB;
  if (!dsn) {
    return null;
  }

  try {
    const Sentry = await import('@sentry/node');
    Sentry.init({
      dsn,
      environment: process.env.SENTRY_ENVIRONMENT || process.env.VITE_SENTRY_ENVIRONMENT || 'development',
      tracesSampleRate: Number(process.env.SENTRY_TRACES_SAMPLE_RATE_WEB || process.env.VITE_SENTRY_TRACES_SAMPLE_RATE || '0'),
      beforeSend(event) {
        return scrubEvent(event);
      },
      sendDefaultPii: false,
    });
    return Sentry;
  } catch {
    return null;
  }
}

function scrubEvent(payload) {
  if (Array.isArray(payload)) {
    return payload.map(scrubEvent);
  }
  if (payload && typeof payload === 'object') {
    return Object.fromEntries(
      Object.entries(payload).map(([key, value]) => {
        const lowered = key.toLowerCase();
        if (['authorization', 'password', 'token', 'content', 'prompt', 'secret', 'jwt'].some((token) => lowered.includes(token))) {
          return [key, '[Filtered]'];
        }
        return [key, scrubEvent(value)];
      }),
    );
  }
  return payload;
}

const sentry = await createNodeSentry();

app.use(compression());

app.get('/robots.txt', (_req, res) => {
  res.setHeader('Content-Type', 'text/plain; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=3600');
  res.send(`User-agent: *\nAllow: /\nSitemap: ${appBaseUrl}/sitemap.xml\n`);
});

app.get('/sitemap.xml', (_req, res) => {
  res.setHeader('Content-Type', 'application/xml; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=3600');
  res.send(renderSitemap());
});

let vite;
let template;
let render;

if (!isProd) {
  const { createServer } = await import('vite');
  vite = await createServer({
    root: __dirname,
    server: { middlewareMode: true },
    appType: 'custom',
  });
  app.use(vite.middlewares);
} else {
  app.use(
    '/assets',
    express.static(resolve('dist/client/assets'), {
      immutable: true,
      maxAge: '1y',
    }),
  );
  app.use(
    express.static(resolve('dist/client'), {
      index: false,
      immutable: true,
      maxAge: '1y',
    }),
  );
  template = await readFile(resolve('dist/client/index.html'), 'utf-8');
  ({ render } = await import('./dist/server/entry-server.js'));
}

app.use(async (req, res) => {
  const url = req.originalUrl;
  try {
    if (!shouldSsr(req.path)) {
      const spaTemplate = isProd
        ? template
        : await vite.transformIndexHtml(url, await readFile(resolve('index.html'), 'utf-8'));
      res.setHeader('Cache-Control', 'no-store');
      res.status(200).send(spaTemplate.replace('<!--app-head-->', defaultHead()).replace('<!--app-html-->', ''));
      return;
    }

    let htmlTemplate;
    let renderFn;
    if (!isProd) {
      htmlTemplate = await readFile(resolve('index.html'), 'utf-8');
      htmlTemplate = await vite.transformIndexHtml(url, htmlTemplate);
      renderFn = (await vite.ssrLoadModule('/src/entry-server.ts')).render;
    } else {
      htmlTemplate = template;
      renderFn = render;
    }

    const rendered = await renderFn(url);
    const html = htmlTemplate
      .replace('<!--app-head-->', rendered.head || defaultHead())
      .replace('<!--app-html-->', rendered.html || '');

    res.setHeader('Cache-Control', 'public, max-age=300');
    res.status(rendered.status || 200).send(html);
  } catch (error) {
    if (vite) {
      vite.ssrFixStacktrace(error);
    }
    if (sentry?.captureException) {
      sentry.captureException(error);
    }
    res.status(500).send('SSR render failed');
  }
});

app.listen(port, () => {
  console.log(`LessonPilot web server running at http://localhost:${port}`);
});
