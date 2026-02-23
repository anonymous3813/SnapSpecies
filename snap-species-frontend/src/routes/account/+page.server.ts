import type { PageServerLoad } from './$types';

const API = 'http://localhost:8000';

export const load: PageServerLoad = async ({ parent, cookies }) => {
	await parent();
	const token = cookies.get('session');
	if (!token) {
		return { user: null, stats: null, sightings: [] };
	}
	const headers = { Authorization: `Bearer ${token}` };
	try {
		const [meRes, statsRes, sightingsRes] = await Promise.all([
			fetch(`${API}/api/me`, { headers }),
			fetch(`${API}/api/me/stats`, { headers }),
			fetch(`${API}/api/me/sightings`, { headers }),
		]);
		const me = meRes.ok ? await meRes.json() : null;
		const stats = statsRes.ok ? await statsRes.json() : null;
		const sightings = sightingsRes.ok ? await sightingsRes.json() : [];
		const user = me
			? { username: me.email ?? '', name: me.name ?? '', email: me.email ?? '' }
			: null;
		return { user, stats, sightings };
	} catch {
		return { user: null, stats: null, sightings: [] };
	}
};
