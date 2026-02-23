<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { authStore, isLoggedIn, logOut } from '$lib/stores/authStore.svelte';
	import { goto } from '$app/navigation';
	import { POST } from './auth/logout/+server';
	import Logo from '$lib/components/Logo.svelte';

	let { data, children } = $props();

	let hideFooter = $derived(
		page.url.pathname === '/map' ||
			page.url.pathname === '/auth/signup' ||
			page.url.pathname === '/auth/login'
	);
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<!-- Header -->
<nav
	class="fixed inset-x-0 top-0 z-50 flex h-14 items-center justify-between border-b border-stone-200 bg-stone-50/90 px-8 backdrop-blur-md"
>
	<a href="/" class="flex items-center gap-2.5">
		<Logo />
		<span class="font-serif text-[15px] font-semibold tracking-tight text-stone-800"
			>Snap Species</span
		>
	</a>

	<div class="flex items-center gap-0.5">
		<a
			href="/scan"
			class="rounded-md px-3.5 py-1.5 text-sm text-stone-500 transition-colors hover:bg-stone-100 hover:text-stone-800"
			>Scan</a
		>
		<a
			href="/map"
			class="rounded-md px-3.5 py-1.5 text-sm text-stone-500 transition-colors hover:bg-stone-100 hover:text-stone-800"
			>Map</a
		>
		<a
			href="/leaderboard"
			class="rounded-md px-3.5 py-1.5 text-sm text-stone-500 transition-colors hover:bg-stone-100 hover:text-stone-800"
			>Leaderboard</a
		>
	</div>

	<div class="flex w-40 flex-shrink-0 justify-end">
		{#if data.user}
			<div class="flex items-center gap-2">
				<a
					href={`/account`}
					class="flex items-center gap-2 rounded-lg border border-stone-200 px-3.5 py-2 text-sm text-stone-600 transition-colors hover:bg-stone-100 hover:text-stone-900"
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
							d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
						/>
					</svg>
					Account
				</a>
				<form method="POST" action="/auth/logout">
					<button
						type="submit"
						class="font-mono text-sm text-stone-400 transition-colors hover:text-stone-600"
					>
						Sign out
					</button>
				</form>
			</div>
		{:else}
			<a
				href="/auth/login"
				class="flex items-center gap-2 rounded-lg bg-green-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-950"
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
						d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"
					/>
				</svg>
				Sign in
			</a>
		{/if}
	</div>
</nav>

<!-- Main content -->
<main class="overflow-hidden pt-14">
	{@render children()}
</main>

<!-- Footer - hidden on map page & login/signup -->
{#if !hideFooter}
	<footer
		class="mx-auto flex max-w-5xl items-center justify-between border-t border-stone-200 px-8 py-7"
	>
		<div class="flex items-center gap-5">
			<div class="flex items-center gap-2">
				<div class="flex h-6 w-6 items-center justify-center rounded-md bg-green-900">
					<svg width="11" height="11" viewBox="0 0 24 24" fill="white">
						<path
							d="M17 7c0-1.1-.9-2-2-2H9C7.9 5 7 5.9 7 7v1h10V7zm0 2H7v9h10V9zm-5 7a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"
						/>
					</svg>
				</div>
				<span class="font-serif text-sm font-semibold text-stone-700">Snap Species</span>
			</div>
			<span class="font-mono text-xs text-stone-400">Built for wildlife conservation.</span>
		</div>
		<div class="flex gap-6">
			<a
				href="/scan"
				class="font-mono text-xs text-stone-400 transition-colors hover:text-stone-600">Scan</a
			>
			<a href="/map" class="font-mono text-xs text-stone-400 transition-colors hover:text-stone-600"
				>Map</a
			>
			<a
				href="/about"
				class="font-mono text-xs text-stone-400 transition-colors hover:text-stone-600">About</a
			>
		</div>
	</footer>
{/if}
