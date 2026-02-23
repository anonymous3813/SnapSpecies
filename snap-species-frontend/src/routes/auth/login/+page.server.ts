import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	return { redirected: url.searchParams.has('redirect') };
};

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const data = await request.formData();
		const email = data.get('email') as string;
		const password = data.get('password') as string;

		if (!email || !password) {
			return fail(400, { error: 'Please fill in all fields.', email });
		}

		let res;
		try {
			res = await fetch('http://localhost:8000/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password })
			});
		} catch {
			return fail(503, { error: 'Could not reach the server. Try again later.', email });
		}

		if (!res.ok) {
			const body = await res.json();
			return fail(401, { error: body.detail ?? 'Invalid credentials.', email });
		}

		const { access_token } = await res.json();

		cookies.set('session', access_token, {
			path: '/',
			httpOnly: false,
			secure: false,
			sameSite: 'lax',
			maxAge: 60 * 60 * 24 * 7
		});

		redirect(302, '/map');
	}
};
