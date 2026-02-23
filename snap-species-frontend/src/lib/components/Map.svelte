<script>
	import { onMount, onDestroy } from 'svelte';
	import { STATUS_CONFIG } from '$lib/constants';
	import { timestampToReadableDate } from '$lib/utils';
	import SightingCard from '$lib/components/SightingCard.svelte';

	let { sightings = [], center = [20, 0], zoom = 2 } = $props();

	let mapEl = $state(null);
	let map = $state(null);
	let selected = $state(null);
	let filterStatus = $state('all');

	const FILTERS = [
		{ value: 'all', label: 'All' },
		{ value: 'CR', label: 'CR' },
		{ value: 'EN', label: 'EN' },
		{ value: 'VU', label: 'VU' },
		{ value: 'LC', label: 'LC' }
	];

	let data = $derived(sightings);

	let filtered = $derived(
		filterStatus === 'all' ? data : data.filter((s) => s.status === filterStatus)
	);

	function makeIcon(status, isSelected = false) {
		const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.LC;
		const size = isSelected ? 38 : 30;
		const svg = `
      <svg width="${size}" height="${size + 8}" viewBox="0 0 30 38" xmlns="http://www.w3.org/2000/svg">
        <circle cx="15" cy="15" r="13" fill="${cfg.color}" opacity="0.15"/>
        <circle cx="15" cy="15" r="9"  fill="${cfg.color}"/>
        <circle cx="15" cy="15" r="4"  fill="white"/>
        <line   x1="15" y1="24" x2="15" y2="36" stroke="${cfg.color}" stroke-width="2" stroke-linecap="round"/>
      </svg>`;
		return svg;
	}

	let L;
	let markers = {};

	onMount(async () => {
		const leaflet = await import('leaflet');
		await import('leaflet/dist/leaflet.css');
		L = leaflet.default;

		map = L.map(mapEl, {
			center,
			zoom,
			zoomControl: false
		});

		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 19
		}).addTo(map);

		L.control.zoom({ position: 'bottomright' }).addTo(map);

		renderMarkers();
	});

	onDestroy(() => {
		map?.remove();
	});

	function renderMarkers() {
		if (!map || !L) return;

		Object.values(markers).forEach((m) => m.remove());
		markers = {};

		filtered.forEach((s) => {
			const isSelected = selected?.id === s.id;
			const cfg = STATUS_CONFIG[s.status] ?? STATUS_CONFIG.LC;

			const icon = L.divIcon({
				html: makeIcon(s.status, isSelected),
				className: '',
				iconSize: [30, 38],
				iconAnchor: [15, 38],
				popupAnchor: [0, -40]
			});

			const marker = L.marker([s.lat, s.lng], { icon })
				.addTo(map)
				.on('click', () => selectSighting(s));

			markers[s.id] = marker;
		});
	}

	$effect(() => {
		filtered;
		selected;
		renderMarkers();
	});

	function selectSighting(s) {
		selected = s;
		map?.flyTo([s.lat, s.lng], Math.max(map.getZoom(), 6), { duration: 0.8 });
	}

	function clearSelection() {
		selected = null;
		renderMarkers();
	}
</script>

<div class="relative flex h-full w-full overflow-hidden bg-white">
	<!-- Sidebar -->
	<aside class="z-10 flex w-72 flex-shrink-0 flex-col border-r border-stone-200 bg-white">
		<!-- Header -->
		<div class="border-b border-stone-200 px-5 py-4">
			<h2 class="mb-3 font-serif text-lg font-semibold text-stone-900">Live Sightings</h2>
			<!-- Filter chips -->
			<div class="flex flex-wrap gap-1.5">
				{#each FILTERS as f}
					<button
						onclick={() => (filterStatus = f.value)}
						class="rounded-full border px-3 py-1 font-mono text-xs transition-colors
              {filterStatus === f.value
							? 'border-green-900 bg-green-900 text-white'
							: 'border-stone-200 bg-white text-stone-500 hover:border-stone-300 hover:text-stone-700'}"
					>
						{f.label}
					</button>
				{/each}
			</div>
		</div>

		<!-- List -->
		<ul class="flex-1 divide-y divide-stone-100 overflow-y-auto">
			{#each filtered as s (s.id)}
				{@const cfg = STATUS_CONFIG[s.status] ?? STATUS_CONFIG.LC}
				<li>
					<button
						onclick={() => selectSighting(s)}
						class="w-full px-5 py-4 text-left transition-colors hover:bg-stone-50
              {selected?.id === s.id
							? 'border-l-2 border-green-800 bg-stone-50'
							: 'border-l-2 border-transparent'}"
					>
						<div class="mb-1 flex items-start justify-between gap-2">
							<span class="font-serif text-sm leading-snug font-semibold text-stone-800"
								>{s.name}</span
							>
							<span class="mt-0.5 flex-shrink-0 font-mono text-xs" style="color:{cfg.color}"
								>{timestampToReadableDate(s.timestamp)}</span
							>
						</div>
						<div class="mb-2 font-mono text-xs text-stone-400 italic">{s.sci}</div>
						<div class="flex items-center gap-2">
							<span
								class="rounded border px-2 py-0.5 font-mono text-xs font-medium"
								style="color:{cfg.color};background:{cfg.bg};border-color:{cfg.border}"
							>
								{s.status}
							</span>
							<span class="font-mono text-xs text-stone-400">{s.threat_score}% match</span>
						</div>
					</button>
				</li>
			{:else}
				<li class="px-5 py-10 text-center text-sm text-stone-400 font-mono">
					No sightings for this filter.
				</li>
			{/each}
		</ul>

		<!-- Sidebar footer-->
		<div class="border-t border-stone-200 bg-stone-50 px-5 py-3">
			<p class="font-mono text-xs text-stone-400">
				{filtered.length} sighting{filtered.length !== 1 ? 's' : ''}
				{filterStatus !== 'all' ? `· ${filterStatus} only` : '· all statuses'}
			</p>
		</div>
	</aside>

	<!-- Map -->
	<div class="relative flex-1">
		<div bind:this={mapEl} class="z-0 h-full w-full"></div>

		<!-- Selected species popup panel -->
		{#if selected}
			<SightingCard sighting={selected} onClose={clearSelection} />
		{/if}

		<!-- Legend -->
		<div
			class="absolute top-4 right-4 z-[1000] rounded-xl border border-stone-200 bg-white px-4 py-3 shadow-sm"
		>
			<p class="mb-2.5 font-mono text-xs tracking-widest text-stone-400 uppercase">Status</p>
			<div class="flex flex-col gap-1.5">
				{#each Object.entries(STATUS_CONFIG) as [key, cfg]}
					<div class="flex items-center gap-2">
						<span class="h-2.5 w-2.5 flex-shrink-0 rounded-full" style="background:{cfg.color}"
						></span>
						<span class="font-mono text-xs text-stone-500">{key} — {cfg.label}</span>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>
