<script>
    let { species } = $props();
</script>

<div>
	<p class="mb-4 font-mono text-xs tracking-widest text-stone-400 uppercase">Species result</p>
	<div class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
		<div class="flex items-center gap-3 p-5">
			<div
				class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-slate-100 text-2xl"
			>
				🐆
			</div>
			<div class="min-w-0 flex-1">
				<div class="font-serif text-[15px] leading-snug font-semibold text-stone-900">
					Amur Leopard
				</div>
				<div class="font-mono text-xs text-stone-400 italic">Panthera pardus orientalis</div>
			</div>
			<span
				class="flex-shrink-0 rounded-md border border-red-100 bg-red-50 px-2.5 py-1 font-mono text-xs font-medium text-red-600"
				>CR</span
			>
		</div>

		<div class="border-t border-stone-100"></div>

		<div class="flex flex-col gap-3.5 p-5">
			<div class="flex items-center justify-between">
				<span class="font-mono text-xs text-stone-400">Confidence</span>
				<span class="font-mono text-xs font-medium text-green-700">97.3%</span>
			</div>
			<div class="flex items-center justify-between">
				<span class="font-mono text-xs text-stone-400">Wild population</span>
				<span class="font-mono text-xs text-stone-600">~100 individuals</span>
			</div>
			<div class="flex items-center justify-between">
				<span class="font-mono text-xs text-stone-400">Population trend</span>
				<span class="font-mono text-xs text-red-500">↓ Decreasing</span>
			</div>
			<div class="flex items-center justify-between">
				<span class="font-mono text-xs text-stone-400">Threat score</span>
				<div class="flex items-center gap-2.5">
					<div class="h-1.5 w-20 overflow-hidden rounded-full bg-stone-100">
						<div
							class="h-full w-[72%] rounded-full bg-gradient-to-r from-green-500 via-amber-400 to-red-400"
						></div>
					</div>
					<span class="font-mono text-xs font-medium text-red-500">72 / 100</span>
				</div>
			</div>
			<div class="flex items-center justify-between">
				<span class="font-mono text-xs text-stone-400">Nearby sightings</span>
				<span class="font-mono text-xs text-stone-600">3 within 50 km</span>
			</div>
		</div>

		<div class="border-t border-stone-100"></div>

		<div class="flex gap-2.5 p-4">
			<button
				class="flex-1 rounded-lg bg-green-900 py-2.5 text-xs font-medium text-white transition-colors hover:bg-green-950"
			>
				Submit sighting
			</button>
			<button
				class="rounded-lg border border-stone-200 px-4 py-2.5 text-xs text-stone-500 transition-colors hover:border-stone-300 hover:text-stone-700"
			>
				View on map →
			</button>
		</div>
	</div>
</div>
