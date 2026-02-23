<script lang="ts">
	import { goto } from '$app/navigation';
	import type { ANIMAL_STATUS } from '$lib/constants';
	import { STATUS_CONFIG } from '$lib/constants';

	const API = 'http://localhost:8000';

	interface ScanResult {
		name: string;
		sci: string;
		status: (typeof ANIMAL_STATUS)[keyof typeof ANIMAL_STATUS];
		endangermentLabel: string;
		confidence: number;
		population: string;
		trend: 'Increasing' | 'Stable' | 'Decreasing' | 'Unknown';
		threatScore: number;
		habitat: string;
		threats: string[];
		nearbySightings: number;
		isEndangered?: boolean;
	}

	// Map backend endangerment string to status + threat score
	const ENDANGERMENT_MAP: Record<string, { status: keyof typeof ANIMAL_STATUS; threatScore: number }> = {
		'Critically Endangered': { status: 'CR', threatScore: 95 },
		'Endangered': { status: 'EN', threatScore: 80 },
		'Vulnerable': { status: 'VU', threatScore: 65 },
		'Near Threatened': { status: 'NT', threatScore: 40 },
		'Least Concern': { status: 'LC', threatScore: 20 },
		'Data Deficient': { status: 'LC', threatScore: 30 },
		'Not Evaluated': { status: 'LC', threatScore: 20 }
	};
	function mapEndangerment(endangerment: string): { status: keyof typeof ANIMAL_STATUS; threatScore: number } {
		const key = (endangerment || '').trim();
		return ENDANGERMENT_MAP[key] ?? { status: 'LC', threatScore: 20 };
	}

	function dataUrlToBlob(dataUrl: string): Blob {
		const [head, data] = dataUrl.split(',');
		const mime = head?.match(/data:([^;]+)/)?.[1] ?? 'image/jpeg';
		const bin = atob(data || '');
		const arr = new Uint8Array(bin.length);
		for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
		return new Blob([arr], { type: mime });
	}

	//State
	type Phase = 'idle' | 'preview' | 'scanning' | 'result';

	let phase = $state<Phase>('idle');
	let imageUrl = $state<string | null>(null);
	let result = $state<ScanResult | null>(null);
	let scanError = $state<string | null>(null);
	let openaiQuotaExceeded = $state(false);
	let submitError = $state<string | null>(null);
	let dragOver = $state(false);
	let cameraMode = $state(false);
	let videoEl = $state<HTMLVideoElement | null>(null);
	let canvasEl = $state<HTMLCanvasElement | null>(null);
	let stream = $state<MediaStream | null>(null);
	let scanStep = $state(0);
	let fileInput = $state<HTMLInputElement | null>(null);
	let scanError = $state<string | null>(null);

	const SCAN_STEPS = [
		'Analysing image...',
		'Querying IUCN Red List...',
		'Fetching occurrence data...',
		'Computing threat score...'
	];

<<<<<<< Updated upstream
=======
	const MOCK_RESULT: ScanResult = {
		name: 'Amur Leopard',
		sci: 'Panthera pardus orientalis',
		status: 'CR',
		endangermentLabel: 'Critically Endangered',
		confidence: 97.3,
		population: '~100 individuals',
		trend: 'Decreasing',
		threatScore: 72,
		habitat: 'Temperate broadleaf & mixed forests',
		threats: ['Habitat loss', 'Poaching', 'Prey depletion', 'Human–wildlife conflict'],
		nearbySightings: 3,
		isEndangered: true
	};

>>>>>>> Stashed changes
	// File handling
	function handleFile(file: File) {
		if (!file.type.startsWith('image/')) return;
		const reader = new FileReader();
		reader.onload = (e) => {
			imageUrl = e.target?.result as string;
			phase = 'preview';
		};
		reader.readAsDataURL(file);
	}

	function onFileInput(e: Event) {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (file) handleFile(file);
	}

	function onDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		const file = e.dataTransfer?.files[0];
		if (file) handleFile(file);
	}

	// Camera
	async function startCamera() {
		cameraMode = true;
		phase = 'preview';
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
			if (videoEl) videoEl.srcObject = stream;
		} catch {
			cameraMode = false;
			phase = 'idle';
			alert('Camera access denied or unavailable.');
		}
	}

	function capturePhoto() {
		if (!videoEl || !canvasEl) return;
		canvasEl.width = videoEl.videoWidth;
		canvasEl.height = videoEl.videoHeight;
		canvasEl.getContext('2d')!.drawImage(videoEl, 0, 0);
		imageUrl = canvasEl.toDataURL('image/jpeg');
		stopCamera();
		cameraMode = false;
	}

	function stopCamera() {
		stream?.getTracks().forEach((t) => t.stop());
		stream = null;
	}

	// Scan
	async function startScan() {
		phase = 'scanning';
		scanStep = 0;
		scanError = null;
<<<<<<< Updated upstream
		openaiQuotaExceeded = false;
=======
		result = null;

>>>>>>> Stashed changes
		for (let i = 0; i < SCAN_STEPS.length; i++) {
			scanStep = i;
			await sleep(400);
		}
		try {
			const formData = new FormData();
			const blob = dataUrlToBlob(imageUrl!);
			formData.append('file', blob, 'image.jpg');
			const res = await fetch(`${API}/identify`, { method: 'POST', body: formData });
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail ?? 'Identification failed');
			}
			const data = await res.json();
			const { status, threatScore: fallbackScore } = mapEndangerment(data.endangerment ?? '');
			const threatScore =
				typeof data.threat_score === 'number' && data.threat_score >= 0 && data.threat_score <= 100
					? data.threat_score
					: fallbackScore;
			const rawTrend = (data.trend ?? '').trim();
			const trend = ['Increasing', 'Stable', 'Decreasing', 'Unknown'].includes(rawTrend)
				? rawTrend
				: 'Unknown';
			result = {
				name: data.species ?? 'Unknown',
				sci: data.sci ?? data.species ?? 'Unknown',
				status,
				confidence: 0,
				population: data.population ?? 'Unknown',
				trend: trend as 'Increasing' | 'Stable' | 'Decreasing' | 'Unknown',
				threatScore,
				habitat: data.habitat ?? 'Unknown',
				threats: Array.isArray(data.threats) ? data.threats : [],
				nearbySightings: 0
			};
			if (data.openaiQuotaExceeded) openaiQuotaExceeded = true;
			phase = 'result';
		} catch (e) {
			scanError = e instanceof Error ? e.message : 'Scan failed';
			phase = 'result';
		}
	}

<<<<<<< Updated upstream
	async function submitSightingToMap() {
		if (!result) return;
		submitError = null;
		let lat = 0;
		let lng = 0;
		if (typeof navigator !== 'undefined' && navigator.geolocation) {
			try {
				const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
					navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000, maximumAge: 60000 });
				});
				lat = pos.coords.latitude;
				lng = pos.coords.longitude;
			} catch {
				// use 0,0
			}
		}
		try {
			const res = await fetch('/scan/submit-sighting', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					name: result.name,
					sci: result.sci,
					status: result.status,
					lat,
					lng,
					threat_score: result.threatScore
				})
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				submitError = err.error ?? 'Could not save sighting. Sign in and try again.';
				return;
			}
			goto('/map');
		} catch {
			submitError = 'Could not save sighting. Sign in and try again.';
		}
=======
		try {
			const blob = await (await fetch(imageUrl!)).blob();
			const formData = new FormData();
			formData.append('image', blob, 'image.jpg');
			if (typeof navigator !== 'undefined' && navigator.geolocation) {
				try {
					const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
						navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000, maximumAge: 60000 });
					});
					formData.append('lat', String(pos.coords.latitude));
					formData.append('lng', String(pos.coords.longitude));
				} catch {
					// continue without location
				}
			}
			const headers: Record<string, string> = {};
			const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
			if (token) headers['Authorization'] = `Bearer ${token}`;
			const res = await fetch('http://localhost:8000/api/scan', {
				method: 'POST',
				body: formData,
				headers
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail ?? 'Scan failed');
			}
			const data = await res.json();
			result = {
				name: data.name,
				sci: data.sci,
				status: data.status,
				endangermentLabel: data.endangermentLabel ?? (data.isEndangered ? 'Endangered' : 'Not endangered'),
				confidence: data.confidence,
				population: data.population ?? 'Unknown',
				trend: data.trend ?? 'Unknown',
				threatScore: data.threatScore,
				habitat: data.habitat ?? 'Unknown',
				threats: Array.isArray(data.threats) ? data.threats : [],
				nearbySightings: data.nearbySightings ?? 0,
				isEndangered: Boolean(data.isEndangered),
				description: data.description ?? '',
				savedToMap: Boolean(data.savedToMap),
				openaiQuotaExceeded: Boolean(data.openaiQuotaExceeded)
			};
		} catch (e) {
			console.error(e);
			scanError = e instanceof Error ? e.message : 'Could not reach the server. Is the backend running at http://localhost:8000?';
		}
		phase = 'result';
>>>>>>> Stashed changes
	}

	function reset() {
		phase = 'idle';
		imageUrl = null;
		result = null;
		scanError = null;
<<<<<<< Updated upstream
		openaiQuotaExceeded = false;
		submitError = null;
=======
>>>>>>> Stashed changes
		scanStep = 0;
		stopCamera();
		cameraMode = false;
	}

	function sleep(ms: number) {
		return new Promise((r) => setTimeout(r, ms));
	}

	const trendIcon = { Increasing: '↑', Stable: '→', Decreasing: '↓', Unknown: '?' };
	const trendColor = {
		Increasing: 'text-green-600',
		Stable: 'text-amber-600',
		Decreasing: 'text-red-500',
		Unknown: 'text-stone-400'
	};
</script>

<div class="mx-auto max-w-2xl px-6 py-12">
	<!-- Page header -->
	<div class="mb-10">
		<p class="mb-3 font-mono text-xs tracking-widest text-green-700 uppercase">
			Species identification
		</p>
		<h1 class="font-serif text-4xl leading-tight font-semibold tracking-tight text-stone-900">
			Scan a species
		</h1>
		<p class="mt-3 text-sm leading-relaxed text-stone-500">
			Upload or photograph a species and get IUCN conservation status and threat data instantly.
		</p>
	</div>

	<!--Upload zone -->
	{#if phase === 'idle'}
		<div
			role="button"
			tabindex="0"
			class="relative cursor-pointer rounded-2xl border-2 border-dashed transition-colors duration-200
             {dragOver
				? 'border-green-700 bg-green-50'
				: 'border-stone-300 bg-white hover:border-stone-400 hover:bg-stone-50'}"
			ondragover={(e) => {
				e.preventDefault();
				dragOver = true;
			}}
			ondragleave={() => (dragOver = false)}
			ondrop={onDrop}
			onclick={() => fileInput?.click()}
			onkeydown={(e) => e.key === 'Enter' && fileInput?.click()}
		>
			<div class="flex flex-col items-center justify-center px-8 py-16 text-center">
				<div class="mb-5 flex h-14 w-14 items-center justify-center rounded-xl bg-stone-100">
					<svg
						class="h-6 w-6 text-stone-400"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
						/>
					</svg>
				</div>
				<p class="mb-1 text-sm font-medium text-stone-700">Drop a photo here</p>
				<p class="mb-6 text-xs text-stone-400">JPG, PNG, HEIC up to 20MB</p>
				<div class="flex items-center gap-3">
					<button
						onclick={(e) => {
							e.stopPropagation();
							fileInput?.click();
						}}
						class="rounded-lg bg-green-900 px-4 py-2.5 text-xs font-medium text-white transition-colors hover:bg-green-950"
					>
						Browse files
					</button>
					<span class="text-xs text-stone-400">or</span>
					<button
						onclick={(e) => {
							e.stopPropagation();
							startCamera();
						}}
						class="flex items-center gap-2 rounded-lg border border-stone-200 px-4 py-2.5 text-xs font-medium text-stone-600 transition-colors hover:border-stone-300 hover:text-stone-800"
					>
						<svg
							class="h-3.5 w-3.5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="1.5"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z"
							/>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z"
							/>
						</svg>
						Use camera
					</button>
				</div>
			</div>
			<input
				bind:this={fileInput}
				type="file"
				accept="image/*"
				class="hidden"
				onchange={onFileInput}
			/>
		</div>

		<!-- Camera preview -->
	{:else if phase === 'preview' && cameraMode}
		<div class="overflow-hidden rounded-2xl border border-stone-200 bg-black shadow-sm">
			<video bind:this={videoEl} autoplay playsinline class="aspect-[4/3] w-full object-cover"
			></video>
			<canvas bind:this={canvasEl} class="hidden"></canvas>
			<div class="flex gap-3 bg-white p-4">
				<button
					onclick={capturePhoto}
					class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-green-900 py-3 text-sm font-medium text-white transition-colors hover:bg-green-950"
				>
					<svg
						class="h-4 w-4"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						stroke-width="2"
					>
						<circle cx="12" cy="12" r="9" />
						<circle cx="12" cy="12" r="4" fill="currentColor" />
					</svg>
					Capture photo
				</button>
				<button
					onclick={reset}
					class="rounded-xl border border-stone-200 px-5 py-3 text-sm text-stone-500 transition-colors hover:border-stone-300"
				>
					Cancel
				</button>
			</div>
		</div>

		<!-- Image preview -->
	{:else if phase === 'preview' && !cameraMode}
		<div class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
			<div class="relative">
				<img src={imageUrl!} alt="Species to identify" class="max-h-80 w-full object-cover" />
				<button
					onclick={reset}
					class="absolute top-3 right-3 flex h-8 w-8 items-center justify-center rounded-full bg-black/40 text-lg leading-none text-white backdrop-blur-sm transition-colors hover:bg-black/60"
					aria-label="Remove photo">×</button
				>
			</div>
			<div class="flex gap-3 p-4">
				<button
					onclick={startScan}
					class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-green-900 py-3 text-sm font-medium text-white transition-colors hover:bg-green-950"
				>
					<svg
						class="h-4 w-4"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"
						/>
					</svg>
					Identify species
				</button>
				<button
					onclick={reset}
					class="rounded-xl border border-stone-200 px-5 py-3 text-sm text-stone-500 transition-colors hover:border-stone-300"
				>
					Retake
				</button>
			</div>
		</div>

		<!-- Scanning state -->
	{:else if phase === 'scanning'}
		<div class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
			<img src={imageUrl!} alt="Scanning" class="max-h-56 w-full object-cover opacity-60" />
			<div class="flex flex-col items-center p-8 text-center">
				<!-- Spinner -->
				<div class="relative mb-6 h-14 w-14">
					<svg class="h-14 w-14 animate-spin text-stone-200" viewBox="0 0 24 24" fill="none">
						<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" />
					</svg>
					<svg
						class="absolute inset-0 h-14 w-14 animate-spin text-green-800"
						style="animation-duration:0.8s"
						viewBox="0 0 24 24"
						fill="none"
					>
						<path
							d="M12 2a10 10 0 0110 10"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
						/>
					</svg>
				</div>

				<!-- Step label -->
				<p class="mb-1 font-serif text-lg font-semibold text-stone-800">{SCAN_STEPS[scanStep]}</p>
				<p class="mb-8 font-mono text-xs text-stone-400">
					Step {scanStep + 1} of {SCAN_STEPS.length}
				</p>

				<!-- Pipeline steps -->
				<div class="flex w-full flex-col gap-2">
					{#each SCAN_STEPS as step, i}
						<div
							class="flex items-center gap-3 rounded-lg px-4 py-2.5 text-left transition-colors
                        {i < scanStep ? 'bg-green-50' : i === scanStep ? 'bg-stone-50' : ''}"
						>
							<div
								class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full transition-all
                          {i < scanStep
									? 'bg-green-700'
									: i === scanStep
										? 'animate-pulse bg-stone-200'
										: 'bg-stone-100'}"
							>
								{#if i < scanStep}
									<svg class="h-3 w-3 text-white" viewBox="0 0 12 12" fill="none">
										<path
											d="M2 6l3 3 5-5"
											stroke="currentColor"
											stroke-width="1.5"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								{:else}
									<span
										class="h-1.5 w-1.5 rounded-full {i === scanStep
											? 'bg-green-700'
											: 'bg-stone-300'}"
									></span>
								{/if}
							</div>
							<span
								class="font-mono text-xs {i < scanStep
									? 'text-green-700'
									: i === scanStep
										? 'font-medium text-stone-700'
										: 'text-stone-400'}"
							>
								{step}
							</span>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Result: scan error -->
	{:else if phase === 'result' && scanError}
		<div class="mb-4 rounded-2xl border border-red-200 bg-red-50 p-6">
			<p class="mb-2 font-mono text-sm font-medium text-red-800">Scan failed</p>
			<p class="mb-4 text-sm text-red-700">{scanError}</p>
			<button
				onclick={reset}
				class="rounded-xl border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-100"
			>
				Try again
			</button>
		</div>

		<!-- Results -->
	{:else if phase === 'result' && scanError}
		<div class="mb-4 rounded-2xl border border-red-200 bg-red-50 p-6">
			<p class="mb-2 font-mono text-sm font-medium text-red-800">Scan failed</p>
			<p class="mb-4 text-sm text-red-700">{scanError}</p>
			<p class="mb-4 text-xs text-red-600">Start the backend with: <code class="rounded bg-red-100 px-1 py-0.5">cd snap-species-backend && uvicorn main:app --reload --port 8000</code></p>
			<button
				onclick={reset}
				class="rounded-xl border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-100"
			>
				Try again
			</button>
		</div>
		{:else if phase === 'result' && result}
		{@const cfg = result.isEndangered ? STATUS_CONFIG[result.status] : { color: '#16a34a', bg: '#f0fdf4', border: '#86efac' }}

		{#if openaiQuotaExceeded}
			<div class="mb-4 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-3 font-mono text-sm text-amber-800">
				OpenAI quota exceeded. Population, habitat, and threats may show as Unknown.
			</div>
		{/if}

		<!-- Photo + identity -->
		<div class="mb-4 overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
			<div class="relative">
				<img src={imageUrl!} alt={result.name} class="max-h-64 w-full object-cover" />
				<div
					class="absolute right-3 bottom-3 rounded-full bg-black/50 px-2.5 py-1 font-mono text-xs text-white backdrop-blur-sm"
				>
					{result.confidence}% match
				</div>
			</div>
			<div class="flex items-start justify-between gap-4 p-5">
				<div>
					<h2 class="font-serif text-2xl leading-tight font-semibold text-stone-900">
						{result.name}
					</h2>
					<p class="mt-0.5 mb-3 font-mono text-sm text-stone-400 italic">{result.sci}</p>
					<span
						class="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 font-mono text-xs font-medium"
						style="color:{cfg.color};background:{cfg.bg};border-color:{cfg.border}"
					>
						<span class="h-1.5 w-1.5 flex-shrink-0 rounded-full" style="background:{cfg.color}"
						></span>
						{result.endangermentLabel}
					</span>
					{#if result.isEndangered}
						<p class="mt-2 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 font-mono text-xs font-medium text-red-700">
							Endangered species — counts toward your leaderboard
						</p>
					{:else}
						<p class="mt-2 rounded-lg border border-green-200 bg-green-50 px-3 py-1.5 font-mono text-xs font-medium text-green-700">
							Not endangered (IUCN)
						</p>
					{/if}
				</div>
				<button
					onclick={reset}
					class="flex-shrink-0 rounded-lg border border-stone-200 px-3 py-2 font-mono text-xs text-stone-400 transition-colors hover:border-stone-300 hover:text-stone-600"
				>
					New scan
				</button>
			</div>
		</div>

		<!-- Data grid -->
		<div class="mb-4 grid grid-cols-2 gap-4">
			<!-- Population -->
			<div class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
				<p class="mb-4 font-mono text-xs tracking-widest text-stone-400 uppercase">Population</p>
				<div class="flex flex-col gap-3">
					<div class="flex items-center justify-between">
						<span class="font-mono text-xs text-stone-400">Wild estimate</span>
						<span class="font-mono text-xs font-medium text-stone-700">{result.population}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="font-mono text-xs text-stone-400">Trend</span>
						<span class="font-mono text-xs font-medium {trendColor[result.trend]}">
							{trendIcon[result.trend]}
							{result.trend}
						</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="font-mono text-xs text-stone-400">Nearby sightings</span>
						<span class="font-mono text-xs text-stone-700"
							>{result.nearbySightings} within 50km</span
						>
					</div>
				</div>
			</div>

			<!-- Threat score -->
			<div class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
				<p class="mb-4 font-mono text-xs tracking-widest text-stone-400 uppercase">Threat Score</p>
				<div class="mb-3 flex items-end gap-3">
					<span
						class="font-serif text-5xl leading-none font-semibold
                       {result.threatScore >= 70
							? 'text-red-500'
							: result.threatScore >= 40
								? 'text-amber-500'
								: 'text-green-600'}"
					>
						{result.threatScore}
					</span>
					<span class="mb-1 font-mono text-xs text-stone-400">/ 100</span>
				</div>
				<div class="mb-2 h-1.5 w-full overflow-hidden rounded-full bg-stone-100">
					<div
						class="h-full rounded-full bg-gradient-to-r from-green-500 via-amber-400 to-red-400 transition-all duration-700"
						style="width:{result.threatScore}%"
					></div>
				</div>
				<p
					class="font-mono text-xs {result.threatScore >= 70
						? 'text-red-500'
						: result.threatScore >= 40
							? 'text-amber-500'
							: 'text-green-600'}"
				>
					{result.threatScore >= 70
						? 'High priority'
						: result.threatScore >= 40
							? 'Medium priority'
							: 'Low priority'}
				</p>
			</div>
		</div>

		{#if result.openaiQuotaExceeded}
			<div class="mb-4 rounded-2xl border border-amber-200 bg-amber-50 p-4">
				<p class="font-mono text-xs font-medium text-amber-800">OpenAI quota exceeded</p>
				<p class="mt-1 text-xs text-amber-700">Population, habitat, and description from OpenAI are unavailable. Add billing or wait for quota reset at <a href="https://platform.openai.com/account/billing" target="_blank" rel="noopener" class="underline">platform.openai.com</a>. IUCN data is still shown.</p>
			</div>
		{/if}

		<!-- About / Description (from OpenAI) -->
		{#if result.description}
			<div class="mb-4 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
				<p class="mb-2 font-mono text-xs tracking-widest text-stone-400 uppercase">About</p>
				<p class="text-sm text-stone-600">{result.description}</p>
			</div>
		{/if}

		<!-- Habitat + Threats -->
		<div class="mb-4 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
			<p class="mb-4 font-mono text-xs tracking-widest text-stone-400 uppercase">
				Habitat & Threats
			</p>
			<div class="mb-4 flex items-start justify-between">
				<span class="font-mono text-xs text-stone-400">Habitat</span>
				<span class="max-w-[60%] text-right font-mono text-xs text-stone-600">{result.habitat}</span
				>
			</div>
			<div class="flex items-start gap-3">
				<span class="flex-shrink-0 font-mono text-xs text-stone-400">Threats</span>
				<div class="flex flex-1 flex-wrap justify-end gap-1.5">
					{#each result.threats as threat}
						<span class="rounded-full bg-stone-100 px-2.5 py-1 font-mono text-xs text-stone-600"
							>{threat}</span
						>
					{/each}
				</div>
			</div>
		</div>

		<!-- CTA -->
		<div class="flex flex-col gap-3">
<<<<<<< Updated upstream
			{#if submitError}
				<p class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800">{submitError}</p>
			{/if}
			<div class="flex gap-3">
				<button
					onclick={submitSightingToMap}
					class="flex-1 rounded-xl bg-green-900 py-3.5 text-center text-sm font-medium text-white transition-colors hover:bg-green-950"
				>
					📍 Submit sighting to map
				</button>
=======
			{#if result.savedToMap}
				<p class="rounded-xl border border-green-200 bg-green-50 px-4 py-2 font-mono text-xs text-green-800">
					✓ Sighting saved to the map. View it below.
				</p>
			{:else}
				<p class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-2 font-mono text-xs text-amber-800">
					Sign in to save this sighting to the map and see it on your account.
				</p>
			{/if}
			<div class="flex gap-3">
				<a
					href="/map"
					class="flex-1 rounded-xl bg-green-900 py-3.5 text-center text-sm font-medium text-white transition-colors hover:bg-green-950"
				>
					{result.savedToMap ? 'View on map' : 'View map'}
				</a>
>>>>>>> Stashed changes
				<button
					onclick={reset}
					class="rounded-xl border border-stone-200 px-6 py-3.5 text-sm text-stone-500 transition-colors hover:border-stone-300 hover:text-stone-700"
				>
					Scan another
				</button>
			</div>
		</div>
	{/if}
</div>
