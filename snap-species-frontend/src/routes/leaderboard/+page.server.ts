import type { PageServerLoad } from './$types';

const API = 'http://localhost:8000';

export const load: PageServerLoad = async () => {
	try {
		const res = await fetch(`${API}/api/leaderboard`);
		if (res.ok) {
			const entries = await res.json();
			return { entries: Array.isArray(entries) ? entries : [], error: '' };
		}
	} catch {
		// backend may be down
	}
	return { entries: [], error: 'Could not load leaderboard.' };
};
