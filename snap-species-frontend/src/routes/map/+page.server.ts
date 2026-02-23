import type { PageServerLoad } from './$types';

const API = 'http://localhost:8000';

export const load: PageServerLoad = async () => {
	try {
		const res = await fetch(`${API}/api/sightings`);
		if (res.ok) {
			const data = await res.json();
			return { sightings: Array.isArray(data) ? data : [] };
		}
	} catch {
		// backend may be down
	}
	return { sightings: [] };
};
