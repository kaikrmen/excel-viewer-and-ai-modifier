export async function apiGet(path: string) {
  const r = await fetch(`/api${path}`, {
    method: "GET",
    credentials: "same-origin",
    cache: "no-store",
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function apiPost(path: string, body: BodyInit, csrf: string) {
  const r = await fetch(`/api${path}`, {
    method: "POST",
    headers: { "x-csrf-token": csrf },
    body,
    credentials: "same-origin",
  });
  if (!r.ok) throw new Error(await r.text());
  return r;
}
