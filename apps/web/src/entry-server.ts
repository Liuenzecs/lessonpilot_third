import { renderToString } from '@vue/server-renderer';

import { createLessonPilotApp } from '@/app/createApp';
import { renderSeoHead } from '@/app/seo';
import '@/shared/styles/main.css';

export async function render(url: string) {
  const { app, router } = createLessonPilotApp({ ssr: true });

  await router.push(url);
  await router.isReady();

  const route = router.currentRoute.value;
  const html = await renderToString(app);
  const head = renderSeoHead(route);
  const status = route.name === 'not-found' ? 404 : 200;

  return { html, head, status };
}
