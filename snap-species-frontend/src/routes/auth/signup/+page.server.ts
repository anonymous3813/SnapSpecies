import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const data = await request.formData();
		const username = data.get('username') as string;
		const name = data.get('name') as string;
		const email = data.get('email') as string;
		const password = data.get('password') as string;
		const confirmPassword = data.get('confirmPassword') as string;

		if (!username || !name || !email || !password) {
			return fail(400, { error: 'Please fill in all fields.', username, name, email });
		}

		if (name.trim().split(' ').length < 2) {
			return fail(400, { error: 'Please enter your full name.', username, name, email });
		}

		if (password !== confirmPassword) {
			return fail(400, { error: 'Passwords do not match.', username, name, email });
		}

		let res;
		try {
			res = await fetch('http://localhost:8000/auth/signup', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, name, email, password })
			});
		} catch {
			return fail(503, {
				error: 'Could not reach the server. Try again later.',
				username,
				name,
				email
			});
		}

		if (!res.ok) {
			const body = await res.json();
			return fail(res.status, {
				error: body.detail ?? 'Could not create account.',
				username,
				name,
				email
			});
		}

		const { access_token } = await res.json();

		cookies.set('session', access_token, {
			path: '/',
			httpOnly: true,
			secure: true,
			sameSite: 'lax',
			maxAge: 60 * 60 * 24 * 7
		});

		redirect(302, '/map');
	}
};
