<script lang="ts">
<<<<<<< Updated upstream
  import Map from '$lib/components/Map.svelte';

  let { data } = $props();
  // API returns timestamp in seconds; Map/SightingCard expect milliseconds
  const sightings = $derived(
    (Array.isArray(data?.sightings) ? data.sightings : []).map((s) => ({
      ...s,
      timestamp: s.timestamp < 1e12 ? s.timestamp * 1000 : s.timestamp
    }))
  );
</script>

<div class="h-[calc(100vh-3.5rem)] bg-stone-100">
  <Map {sightings} />
=======
	import Map from '$lib/components/Map.svelte';
	import type { Sighting } from '$lib/types';

	let { data } = $props();

	const sightings = $derived(
		(data.sightings ?? []).map(
			(s: {
				id: number;
				name: string;
				sci: string;
				status: string;
				lat: number;
				lng: number;
				timestamp: number;
				threat_score: number;
				reporter: string;
			}) =>
				({
					id: s.id,
					name: s.name,
					sci: s.sci,
					status: s.status as Sighting['status'],
					lat: s.lat,
					lng: s.lng,
					timestamp: s.timestamp,
					threat_score: s.threat_score,
					reporter: s.reporter
				}) as Sighting
		)
	);
</script>

<div class="h-[calc(100vh-3.5rem)] bg-stone-100">
	<Map {sightings} />
>>>>>>> Stashed changes
</div>