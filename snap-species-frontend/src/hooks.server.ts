import { redirect, type Handle } from '@sveltejs/kit';

const PROTECTED_ROUTES = ['/account', '/scan']; //Need to be logged in to access these routes
const NO_AUTH_ROUTES = ['/auth/login', '/auth/signup']; //Need to be logged out to access these routes

const MOCK_USER = { username: 'jane_doe', email: 'test@example.com' };
const LOGGED_IN = true;

export const handle: Handle = async ({ event, resolve }) => {
  //const token = event.cookies.get('session');
  event.locals.user = LOGGED_IN ? MOCK_USER : null;
  console.log('User from cookie:', event.locals.user);

  /*if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      event.locals.user = {
        username: payload.username,
        email: payload.email,
      };
    } catch {
      event.locals.user = null;
      event.cookies.delete('session', { path: '/' });
    }
  } else {
    event.locals.user = null;
  }*/
  
  const isProtected = PROTECTED_ROUTES.some(path => event.url.pathname.startsWith(path));
  if (isProtected && !event.locals.user) {
    console.log(event.locals.user, 'User is not authenticated, redirecting to login');
    redirect(302, '/auth/login?redirect=' + encodeURIComponent(event.url.pathname));
  }

  const isNoAuth = NO_AUTH_ROUTES.some(path => event.url.pathname.startsWith(path));
  if (isNoAuth && event.locals.user) {
    redirect(302, '/map');
  }

  return resolve(event);
};