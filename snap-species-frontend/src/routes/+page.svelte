<script>
	import SightingCard from '$lib/components/SightingCard.svelte';
    import mapDemo from '$lib/assets/map-demo.png';
	import { onMount } from 'svelte';

	let mounted = false;
	onMount(() => setTimeout(() => (mounted = true), 60));

	const stats = [
		{ num: '1+', label: 'Species tracked' },
		{ num: '47K', label: 'Endangered Species' },
		{ num: '28%', label: 'Species threatened' },
		{ num: '150/day', label: 'Species lost' }
	];

    const citations = ['IUCN Red List', 'GBIF', 'iNaturalist', 'OpenStreetMap']

	const steps = [
		{
			n: '01',
			title: 'Photograph',
			desc: 'Upload or snap a photo of any animal, plant, or bird in the wild.'
		},
		{
			n: '02',
			title: 'Identify',
			desc: 'Claude Vision identifies the species and pulls live IUCN + GBIF data.'
		},
		{
			n: '03',
			title: 'Score',
			desc: 'Our algorithm outputs a 0–100 threat score based on status and location.'
		},
		{
			n: '04',
			title: 'Contribute',
			desc: 'Pin your sighting to the shared map and join the citizen science network.'
		}
	];

	const features = [
		{
			tag: '01',
			title: 'AI Identification',
			desc: "Photograph any species and get an instant ID with confidence scoring, cross-referenced against iNaturalist's 50M+ observations."
		},
		{
			tag: '02',
			title: 'Conservation Status',
			desc: 'Live IUCN Red List data on every result — population trends, habitat range, and active threat factors pulled in real time.'
		},
		{
			tag: '03',
			title: 'Threat Scoring',
			desc: 'A custom algorithm weighs IUCN listing, population decline, and sighting location to produce an actionable priority score.'
		},
		{
			tag: '04',
			title: 'Live Sighting Map',
			desc: 'Every confirmed sighting is pinned to a shared map. Alerts fire when endangered species appear outside known ranges.'
		}
	];
</script>

<!-- HERO -->
<section
	class="mx-auto max-w-5xl px-8 pt-36 pb-0 text-center transition-all duration-700 ease-out"
	class:opacity-0={!mounted}
	class:translate-y-3={!mounted}
	class:opacity-100={mounted}
	class:translate-y-0={mounted}
>
	<!-- Live pill -->
	<div
		class="mb-10 inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3.5 py-1.5 font-mono text-xs text-stone-500 shadow-sm"
	>
		<span class="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-green-600"></span>
		Live · 12 sightings in the last hour
	</div>

	<h1 class="mb-6 font-serif text-6xl leading-[1.07] font-semibold tracking-tight text-stone-900">
		Wildlife intelligence<br />
		for <span class="text-green-800 italic">everyone.</span>
	</h1>

	<p class="mx-auto mb-10 max-w-lg text-base leading-relaxed font-light text-stone-500">
		Point your camera at any species. Get IUCN conservation status, population data, and a real-time
		threat score — instantly.
	</p>

	<div class="mb-20 flex items-center justify-center gap-3">
		<a
			href="/scan"
			class="rounded-lg bg-green-900 px-6 py-3 text-sm font-medium text-white transition-all hover:-translate-y-px hover:bg-green-950"
		>
			Scan a species
		</a>
		<a
			href="/map"
			class="rounded-lg border border-stone-200 bg-white px-5 py-3 text-sm text-stone-500 shadow-sm transition-colors hover:border-stone-300 hover:text-stone-700"
		>
			View live map
		</a>
	</div>

	<!-- Stat strip -->
	<div
		class="grid grid-cols-4 overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm"
	>
		{#each stats as s, i}
			<div class="px-6 py-7 text-left {i < 3 ? 'border-r border-stone-200' : ''}">
				<div
					class="mb-1.5 font-serif text-3xl leading-none font-semibold tracking-tight text-stone-800"
				>
					{s.num}
				</div>
				<div class="font-mono text-xs tracking-wide text-stone-400 uppercase">{s.label}</div>
			</div>
		{/each}
	</div>
</section>

<!-- DEMO + STEPS -->
<section class="mx-auto grid max-w-5xl grid-cols-2 items-stretch gap-6 px-8 py-20">
	<div class="relative overflow-hidden rounded-2xl">
		<img
			src={mapDemo}
			alt="Map demo screenshot"
			aria-hidden="true"
			class="absolute inset-0 h-full w-full object-cover"
		/>

		<SightingCard
			sighting={{
				id: 123,
				name: 'Amur Leopard',
				sci: 'Panthera pardus orientalis',
				status: 'CR',
				conf: 97.3,
				time: '2024-06-21 14:32',
				lat: 43.1,
				lng: 131.9,
				reporter: 'Jane Doe'
			}}
			onClose={() => {}}
            absolute={true}
		/>
	</div>

	<!-- Steps -->
	<div>
		<p class="mb-4 font-mono text-xs tracking-widest text-stone-400 uppercase">How it works</p>
		{#each steps as s, i}
			<div class="flex gap-5 py-6 {i < steps.length - 1 ? 'border-b border-stone-200' : ''}">
				<span class="w-6 flex-shrink-0 pt-0.5 font-mono text-xs font-medium text-green-700"
					>{s.n}</span
				>
				<div>
					<div class="mb-1.5 font-serif text-sm font-semibold text-stone-800">{s.title}</div>
					<div class="text-sm leading-relaxed text-stone-500">{s.desc}</div>
				</div>
			</div>
		{/each}
	</div>
</section>

<!-- FEATURES -->
<section class="mx-auto max-w-5xl px-8 pb-20">
	<div class="mb-10">
		<p class="mb-3 font-mono text-xs tracking-widest text-green-700 uppercase">Capabilities</p>
		<h2 class="font-serif text-4xl leading-tight font-semibold tracking-tight text-stone-900">
			Everything you need to<br />
			<span class="text-green-800 italic">document the wild.</span>
		</h2>
	</div>

	<div
		class="grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-stone-200 bg-stone-200"
	>
		{#each features as f}
			<div class="group relative overflow-hidden bg-white p-8 transition-colors hover:bg-stone-50">
				<div
					class="absolute right-8 bottom-0 left-8 h-px origin-left scale-x-0 bg-green-700 transition-transform duration-300 group-hover:scale-x-100"
				></div>
				<p class="mb-5 font-mono text-xs font-medium text-green-700">{f.tag}</p>
				<h3 class="mb-3 font-serif text-lg font-semibold text-stone-800">{f.title}</h3>
				<p class="text-sm leading-relaxed text-stone-500">{f.desc}</p>
			</div>
		{/each}
	</div>
</section>

<!-- DATA SOURCES -->
<section class="mx-auto max-w-5xl px-8 pb-20 text-center">
	<p class="mb-5 font-mono text-xs tracking-widest text-stone-400 uppercase">
		Powered by open data
	</p>
	<div class="flex flex-wrap justify-center gap-2.5">
		{#each citations as chip}
			<span
				class="cursor-default rounded-full border border-stone-200 bg-white px-4 py-2 font-mono text-xs text-stone-500 shadow-sm transition-colors hover:border-stone-300 hover:text-stone-700"
			>
				{chip}
			</span>
		{/each}
	</div>
</section>

<!-- CTA -->
<section class="mx-auto max-w-5xl px-8 pb-24">
	<div
		class="relative grid grid-cols-2 items-center gap-16 overflow-hidden rounded-2xl bg-green-900 p-16"
	>
		<div
			class="pointer-events-none absolute inset-0 opacity-[0.07]"
			style="background-image:radial-gradient(circle,#fff 1px,transparent 1px);background-size:22px 22px"
		></div>
		<div class="relative">
			<p class="mb-4 font-mono text-xs tracking-widest text-green-300 uppercase">
				Free · Open source · No account required
			</p>
			<h2 class="font-serif text-4xl leading-tight font-semibold tracking-tight text-white">
				Every sighting<br />
				<span class="text-green-300 italic">matters.</span>
			</h2>
		</div>
		<div class="relative">
			<p class="mb-7 text-base leading-relaxed font-light text-green-200">
				Join thousands of citizen scientists tracking endangered species worldwide. No expertise
				needed — just a camera.
			</p>
			<a
				href="/scan"
				class="inline-flex items-center rounded-lg bg-white px-6 py-3.5 text-sm font-medium text-green-900 transition-all hover:-translate-y-px hover:bg-stone-50"
			>
				Scan your first species →
			</a>
		</div>
	</div>
</section>
