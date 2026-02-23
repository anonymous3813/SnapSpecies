export interface Sighting {
	id: number;
	name: string;
	sci: string;
	status: 'CR' | 'EN' | 'VU' | 'NT' | 'LC';
	lat: number;
	lng: number;
	timestamp: number;
	threat_score: number;
	reporter: string;
}

export interface User {
	username: string;
	name?: string;
	email: string;
}

export interface LeaderboardEntry {
	rank: number;
	name: string;
	score: number;
	species: number;
	endangered_species: number;
	avg_threat_score: number;
	joined: string;
}

export interface UserStats {
	endangered_species: number;
	total_sightings: number;
	avg_threat_score: number;
}
