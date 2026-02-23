<script lang="ts">
	import type { LeaderboardEntry } from '$lib/types';

<<<<<<< Updated upstream
	let { data } = $props();
=======
	// Sample data — remove once backend is ready
	const SAMPLE: LeaderboardEntry[] = [
		{ rank: 1, name: 'Jane Doe', score: 9840, species: 142, endangered_species: 12, avg_threat_score: 72.5, joined: 'Jan 2024' },
		{ rank: 2, name: 'Tariq Hassan', score: 8210, species: 118, endangered_species: 10, avg_threat_score: 68.2, joined: 'Feb 2024' },
		{ rank: 3, name: 'Mei Lin', score: 7640, species: 97, endangered_species: 8, avg_threat_score: 65.0, joined: 'Mar 2024' },
		{ rank: 4, name: 'Samuel Osei', score: 6310, species: 84, endangered_species: 6, avg_threat_score: 58.3, joined: 'Jan 2024' },
		{ rank: 5, name: 'Priya Nair', score: 5490, species: 76, endangered_species: 5, avg_threat_score: 52.1, joined: 'Apr 2024' },
		{ rank: 6, name: 'Erik Lindström', score: 4870, species: 61, endangered_species: 4, avg_threat_score: 48.0, joined: 'May 2024' },
		{ rank: 7, name: 'Amara Diallo', score: 4120, species: 55, endangered_species: 3, avg_threat_score: 45.2, joined: 'Apr 2024' },
		{ rank: 8, name: 'Lucas Ferreira', score: 3660, species: 48, endangered_species: 2, avg_threat_score: 42.0, joined: 'Jun 2024' },
		{ rank: 9, name: 'Yuki Tanaka', score: 3140, species: 43, endangered_species: 2, avg_threat_score: 38.5, joined: 'May 2024' },
		{ rank: 10, name: 'Sofia Rossi', score: 2890, species: 38, endangered_species: 1, avg_threat_score: 35.0, joined: 'Jun 2024' }
	];
>>>>>>> Stashed changes

	const entries = $derived(Array.isArray(data?.entries) ? data.entries : []) as LeaderboardEntry[];
	const loading = $derived(typeof data === 'undefined');
	const error = $derived((data?.error as string) ?? '');

	const topScore = $derived(entries[0]?.score ?? 1);

	const podiumOrder = $derived(
		entries.length >= 3 ? [entries[1], entries[0], entries[2]] : entries.slice(0, 3)
	);

	const PODIUM_META = [
		{ height: 'h-20', label: '2nd', color: 'bg-stone-200', text: 'text-stone-500' },
		{ height: 'h-28', label: '1st', color: 'bg-green-900', text: 'text-white' },
		{ height: 'h-16', label: '3rd', color: 'bg-amber-100', text: 'text-amber-700' }
	];
<<<<<<< Updated upstream
=======

	onMount(async () => {
		try {
			const res = await fetch('http://localhost:8000/api/leaderboard');
			if (res.ok) {
				const data = await res.json();
				entries = Array.isArray(data)
					? data.map((e: LeaderboardEntry) => ({
							...e,
							endangered_species: e.endangered_species ?? 0,
							avg_threat_score: e.avg_threat_score ?? 0
						}))
					: SAMPLE;
			} else {
				entries = SAMPLE;
			}
		} catch {
			entries = SAMPLE;
		} finally {
			loading = false;
		}
	});
>>>>>>> Stashed changes
</script>

<div class="mx-auto max-w-3xl px-8 py-14">
	<!-- Header -->
	<div class="p-8">
		<p
			class="mb-4 flex items-center gap-2 font-mono text-xs tracking-[0.25em] text-green-600 uppercase"
		>
			<span class="inline-block h-px w-6 bg-green-600"></span>
			Community
		</p>
		<div class="flex items-start justify-between gap-8">
			<div>
				<h1
					class="mb-4 font-serif text-5xl leading-none font-semibold tracking-tight text-stone-900"
				>
					Leaderboard
				</h1>
				<p class="max-w-xs text-sm leading-relaxed text-stone-500">
					Ranked by number of endangered species found and average endangerment score.
				</p>
			</div>
			<a
				href="/scan"
				class="mt-1 flex flex-shrink-0 items-center gap-1.5 rounded-xl bg-green-900 px-5 py-3
               text-sm font-medium whitespace-nowrap text-white transition-all
               hover:-translate-y-0.5 hover:bg-green-950 hover:shadow-lg hover:shadow-green-900/20"
			>
				Add a sighting
				<span class="text-base leading-none text-green-400">→</span>
			</a>
		</div>
	</div>

	{#if loading}
		<!-- Skeleton -->
		<div class="flex flex-col gap-3">
			{#each Array(7) as _}
				<div class="h-16 animate-pulse rounded-xl bg-stone-200"></div>
			{/each}
		</div>
	{:else if error}
		<div
			class="rounded-xl border border-red-100 bg-red-50 px-5 py-4 font-mono text-sm text-red-500"
		>
			{error}
		</div>
	{:else}
		<!-- Podium -->
		<div class="mb-8 flex items-end justify-center gap-3">
			{#each podiumOrder as entry, i}
				{@const meta = PODIUM_META[i]}
				<div class="flex w-36 flex-col items-center gap-2">
					<!-- Name + score above podium -->
					<div class="text-center">
						<div class="font-serif text-sm leading-snug font-semibold text-stone-800">
							{entry.name}
						</div>
						<div class="mt-0.5 font-mono text-xs text-stone-400">
							{entry.endangered_species} endangered · avg {entry.avg_threat_score}
						</div>
					</div>
					<!-- Podium block -->
					<div
						class="{meta.height} w-full {meta.color} flex items-center justify-center rounded-t-xl"
					>
						<span class="font-mono text-sm font-semibold {meta.text}">{meta.label}</span>
					</div>
				</div>
			{/each}
		</div>

		<!-- Divider -->
		<div class="mb-6 border-t border-stone-200"></div>

		<!-- Full list -->
		<div
			class="flex flex-col gap-px overflow-hidden rounded-2xl border border-stone-200 bg-stone-200"
		>
			{#each entries as entry}
				<div class="flex items-center gap-5 bg-white px-6 py-4 transition-colors hover:bg-stone-50">
					<!-- Rank -->
					<span
						class="w-5 flex-shrink-0 text-right font-mono text-sm
                       {entry.rank <= 3 ? 'font-medium text-green-700' : 'text-stone-400'}"
					>
						{entry.rank}
					</span>

					<!-- Name -->
					<span class="min-w-0 flex-1 truncate font-serif text-sm font-semibold text-stone-800">
						{entry.name}
					</span>

					<!-- Bar -->
					<div class="h-1.5 w-32 flex-shrink-0 overflow-hidden rounded-full bg-stone-100">
						<div
							class="h-full rounded-full bg-green-700 transition-all duration-700"
							style="width: {(entry.score / topScore) * 100}%"
						></div>
					</div>

					<!-- Score -->
					<div class="flex-shrink-0 text-right">
						<span class="font-mono text-sm font-medium text-stone-800">
							{entry.score.toLocaleString()}
						</span>
						<span class="ml-1 font-mono text-xs text-stone-400">pts</span>
					</div>

					<!-- Endangered + avg score -->
					<div class="w-28 flex-shrink-0 text-right">
						<span class="font-mono text-xs text-red-600">{entry.endangered_species} endangered</span>
						<span class="block font-mono text-xs text-stone-400">avg {entry.avg_threat_score}</span>
					</div>
				</div>
			{/each}
		</div>

		<!-- Score explanation -->
		<div class="mt-6 rounded-xl border border-stone-200 bg-stone-50 px-5 py-4">
			<p class="mb-2 font-mono text-xs tracking-widest text-stone-400 uppercase">How scores work</p>
			<p class="text-xs leading-relaxed text-stone-500">
				Ranking is by number of distinct endangered species (CR, EN, VU) you have found, then by
				average endangerment score across all your sightings. Finding an endangered species
				increases your count and updates your leaderboard position.
			</p>
		</div>
	{/if}
</div>
