import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const API = 'http://localhost:8000';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const token = cookies.get('session');
	if (!token) {
		return json({ error: 'Not authenticated' }, { status: 401 });
	}
	let body: { name: string; sci: string; status: string; lat?: number; lng?: number; threat_score?: number };
	try {
		body = await request.json();
	} catch {
		return json({ error: 'Invalid body' }, { status: 400 });
	}
	if (!body?.name || !body?.sci) {
		return json({ error: 'name and sci required' }, { status: 400 });
	}
	const res = await fetch(`${API}/api/sightings`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`,
		},
		body: JSON.stringify({
			name: body.name,
			sci: body.sci,
			status: body.status || 'LC',
			lat: typeof body.lat === 'number' ? body.lat : 0,
			lng: typeof body.lng === 'number' ? body.lng : 0,
			threat_score: typeof body.threat_score === 'number' ? body.threat_score : 0,
		}),
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		return json(err, { status: res.status });
	}
	const data = await res.json();
	return json(data);
};
