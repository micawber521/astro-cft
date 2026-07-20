import type { APIRoute } from 'astro';

export const prerender = false;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function page(title: string, message: string) {
  return `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>${title}</title>
<style>
  body { font-family: -apple-system, sans-serif; background:#0e2c52; color:#f5f0e6;
         display:flex; align-items:center; justify-content:center; height:100vh; margin:0; text-align:center; }
  a { color:#e3c25c; }
  .box { max-width: 420px; padding: 0 24px; }
</style></head>
<body><div class="box"><p>${message}</p><p><a href="/">&larr; Back to CFTrust</a></p></div></body></html>`;
}

export const POST: APIRoute = async ({ request, locals }) => {
  const form = await request.formData();
  const email = String(form.get('email') || '').trim().toLowerCase();
  const honeypot = String(form.get('website') || '');

  // Bots fill every field, including ones hidden from humans via CSS.
  if (honeypot) {
    return new Response(page('Subscribed', "Thanks — you're on the list."), {
      status: 200,
      headers: { 'Content-Type': 'text/html' },
    });
  }

  if (!EMAIL_RE.test(email)) {
    return new Response(page('Invalid email', 'That doesn\'t look like a valid email address. Please go back and try again.'), {
      status: 400,
      headers: { 'Content-Type': 'text/html' },
    });
  }

  const kv = (locals as any)?.runtime?.env?.SUBSCRIBERS;
  if (!kv) {
    return new Response(page('Unavailable', 'Signup is temporarily unavailable — please try again later.'), {
      status: 500,
      headers: { 'Content-Type': 'text/html' },
    });
  }

  // Keyed by email so a resubmission just overwrites instead of erroring or duplicating.
  await kv.put(email, JSON.stringify({ email, subscribedAt: new Date().toISOString() }));

  return new Response(page('Subscribed', "Thanks — you're on the list. You'll hear from us when there's something new."), {
    status: 200,
    headers: { 'Content-Type': 'text/html' },
  });
};
