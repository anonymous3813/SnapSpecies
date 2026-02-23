import { redirect, type Handle } from '@sveltejs/kit';

const PROTECTED_ROUTES = ['/account', '/scan'];
const NO_AUTH_ROUTES = ['/auth/login', '/auth/signup'];
<<<<<<< Updated upstream
const API = 'http://localhost:8000';
=======
>>>>>>> Stashed changes

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('session');
  event.locals.user = null;
  if (token) {
    try {
<<<<<<< Updated upstream
      const res = await fetch(`${API}/api/me`, {
=======
      const res = await fetch('http://localhost:8000/api/me', {
>>>>>>> Stashed changes
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const user = await res.json();
        event.locals.user = {
          username: user.email ?? '',
          name: user.name ?? '',
          email: user.email ?? '',
        };
      }
    } catch {
      event.locals.user = null;
    }
  }

  const isProtected = PROTECTED_ROUTES.some((path) => event.url.pathname.startsWith(path));
  if (isProtected && !event.locals.user) {
    redirect(302, '/auth/login?redirect=' + encodeURIComponent(event.url.pathname));
  }

  const isNoAuth = NO_AUTH_ROUTES.some((path) => event.url.pathname.startsWith(path));
  if (isNoAuth && event.locals.user) {
    redirect(302, '/map');
  }

  return resolve(event);
};