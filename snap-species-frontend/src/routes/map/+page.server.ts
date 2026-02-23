import type { PageServerLoad } from './$types';

<<<<<<< Updated upstream
const API = 'http://localhost:8000';

export const load: PageServerLoad = async () => {
	try {
		const res = await fetch(`${API}/api/sightings`);
=======
export const load: PageServerLoad = async () => {
	try {
		const res = await fetch('http://localhost:8000/api/sightings');
>>>>>>> Stashed changes
		if (res.ok) {
			const data = await res.json();
			return { sightings: Array.isArray(data) ? data : [] };
		}
	} catch {
		// backend may be down
	}
	return { sightings: [] };
};
