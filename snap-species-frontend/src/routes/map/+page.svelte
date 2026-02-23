<script lang="ts">
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
</div>