<script lang="ts">
	import { STATUS_CONFIG } from '$lib/constants';
	import type { Sighting } from '$lib/types';
    import { timestampToReadableDate } from '$lib/utils';

	let { sighting, onClose, absolute = true }: { sighting: Sighting; onClose: () => void; absolute?: boolean } = $props();

	let cfg = $derived(STATUS_CONFIG[sighting.status] ?? STATUS_CONFIG.LC);
</script>

<div
	class="{absolute ? 'absolute bottom-6 left-6 z-[40]' : ''} w-72 overflow-hidden rounded-xl border border-stone-200 bg-white shadow-lg"
>
	<div class="flex items-center justify-between border-b border-stone-100 px-4 py-3">
		<div>
			<div class="font-serif text-sm leading-snug font-semibold text-stone-900">
				{sighting.name}
			</div>
			<div class="font-mono text-xs text-stone-400 italic">{sighting.sci}</div>
		</div>
		<button
			onclick={onClose}
			class="ml-2 flex-shrink-0 text-lg leading-none text-stone-400 hover:text-stone-600"
			aria-label="Close">×</button
		>
	</div>
	<div class="flex flex-col gap-2.5 px-4 py-3">
		<div class="flex items-center justify-between">
			<span class="font-mono text-xs text-stone-400">Status</span>
			<span
				class="rounded border px-2 py-0.5 font-mono text-xs font-medium"
				style="color:{cfg.color};background:{cfg.bg};border-color:{cfg.border}"
			>
				{cfg.label}
			</span>
		</div>
		<div class="flex items-center justify-between">
			<span class="font-mono text-xs text-stone-400">Threat score</span>
			<span class="font-mono text-xs font-medium text-green-700">{sighting.threat_score}%</span>
		</div>
		<div class="flex items-center justify-between">
			<span class="font-mono text-xs text-stone-400">Reported</span>
			<span class="font-mono text-xs text-stone-600">{timestampToReadableDate(sighting.timestamp)}</span>
		</div>
		<div class="flex items-center justify-between">
			<span class="font-mono text-xs text-stone-400">Coordinates</span>
			<span class="font-mono text-xs text-stone-600"
				>{sighting.lat.toFixed(2)}, {sighting.lng.toFixed(2)}</span
			>
		</div>
	</div>
	<div class="px-4 pb-3">
		<a
			href="/result/{sighting.id}"
			class="block w-full rounded-lg bg-green-900 py-2.5 text-center text-xs font-medium text-white transition-colors hover:bg-green-950"
		>
			View full report →
		</a>
	</div>
</div>
