<script lang="ts">
	import { goto } from '$app/navigation';

    let username = $state('');
	let name = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');

	async function submit() {
		error = '';
		if (!name || !email || !password) {
			error = 'Please fill in all fields.';
			return;
		}
        if (name.trim().split(' ').length < 2) {
            error = 'Please enter your full name.';
            return;
        }
        if (password !== confirmPassword) {
            error = 'Passwords do not match.';
            return;
        }
		loading = true;
		try {
			const res = await fetch('http://localhost:8000/auth/signup', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name, email, password })
			});
			if (!res.ok) {
				error = (await res.json()).detail ?? 'Could not create account.';
				return;
			}
			localStorage.setItem('token', (await res.json()).access_token);
			goto('/map');
		} catch {
			error = 'Could not reach the server.';
		} finally {
			loading = false;
		}
	}
</script>

<div class="w-[360px] rounded-2xl border border-stone-200 bg-white p-8 shadow-sm">
	<!-- Header -->
	<div class="mb-7 flex flex-col items-center gap-3 text-center">
		<div class="flex h-11 w-11 items-center justify-center rounded-xl bg-green-900">
			<svg width="20" height="20" viewBox="0 0 24 24" fill="white">
				<path
					d="M17 7c0-1.1-.9-2-2-2H9C7.9 5 7 5.9 7 7v1h10V7zm0 2H7v9h10V9zm-5 7a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"
				/>
			</svg>
		</div>
		<div>
			<h2 class="font-serif text-xl font-semibold text-stone-900">Create account</h2>
			<p class="mt-0.5 text-xs text-stone-400">Join the citizen science network</p>
		</div>
	</div>

	<!-- Form -->
	<form
		onsubmit={(e) => {
			e.preventDefault();
			submit();
		}}
		class="flex flex-col gap-4"
	>
        <div class="flex flex-col gap-1.5">
			<label for="name" class="font-mono text-xs tracking-wider text-stone-400 uppercase"
				>Username</label
			>
			<input
				id="username"
				type="text"
				bind:value={username}
				placeholder="JaneDoe123"
				class="rounded-lg border border-stone-200 bg-stone-50 px-3.5 py-2.5 text-sm text-stone-800
               transition-colors outline-none placeholder:text-stone-300
               focus:border-green-700 focus:bg-white focus:ring-2 focus:ring-green-700/10"
			/>
		</div>

		<div class="flex flex-col gap-1.5">
			<label for="name" class="font-mono text-xs tracking-wider text-stone-400 uppercase"
				>Full name</label
			>
			<input
				id="name"
				type="text"
				bind:value={name}
				placeholder="Jane Doe"
				class="rounded-lg border border-stone-200 bg-stone-50 px-3.5 py-2.5 text-sm text-stone-800
               transition-colors outline-none placeholder:text-stone-300
               focus:border-green-700 focus:bg-white focus:ring-2 focus:ring-green-700/10"
			/>
		</div>

		<div class="flex flex-col gap-1.5">
			<label for="email" class="font-mono text-xs tracking-wider text-stone-400 uppercase"
				>Email</label
			>
			<input
				id="email"
				type="email"
				bind:value={email}
				placeholder="you@example.com"
				class="rounded-lg border border-stone-200 bg-stone-50 px-3.5 py-2.5 text-sm text-stone-800
               transition-colors outline-none placeholder:text-stone-300
               focus:border-green-700 focus:bg-white focus:ring-2 focus:ring-green-700/10"
			/>
		</div>

		<div class="flex flex-col gap-1.5">
			<label for="password" class="font-mono text-xs tracking-wider text-stone-400 uppercase"
				>Password</label
			>
			<input
				id="password"
				type="password"
				bind:value={password}
				placeholder="••••••••"
				class="rounded-lg border border-stone-200 bg-stone-50 px-3.5 py-2.5 text-sm text-stone-800
               transition-colors outline-none placeholder:text-stone-300
               focus:border-green-700 focus:bg-white focus:ring-2 focus:ring-green-700/10"
			/>
		</div>

		<div class="flex flex-col gap-1.5">
			<label for="confirm-pw" class="font-mono text-xs tracking-wider text-stone-400 uppercase"
				>Confirm Password</label
			>
			<input
				id="confirm-pw"
				type="confirm-pw"
				bind:value={confirmPassword}
				placeholder="••••••••"
				class="rounded-lg border border-stone-200 bg-stone-50 px-3.5 py-2.5 text-sm text-stone-800
               transition-colors outline-none placeholder:text-stone-300
               focus:border-green-700 focus:bg-white focus:ring-2 focus:ring-green-700/10"
			/>
		</div>

		{#if error}
			<p
				class="rounded-lg border border-red-100 bg-red-50 px-3.5 py-2 font-mono text-xs text-red-500"
			>
				{error}
			</p>
		{/if}

		<button
			type="submit"
			disabled={loading}
			class="flex w-full items-center justify-center gap-2 rounded-xl bg-green-900 py-3 text-sm
             font-medium text-white transition-all hover:-translate-y-px hover:bg-green-950
             disabled:cursor-not-allowed disabled:opacity-60"
		>
			{#if loading}
				<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
					<circle cx="12" cy="12" r="10" stroke="white" stroke-width="2" opacity="0.25" />
					<path d="M12 2a10 10 0 0110 10" stroke="white" stroke-width="2" stroke-linecap="round" />
				</svg>
				Creating account...
			{:else}
				Create account
			{/if}
		</button>
	</form>

	<p class="mt-6 text-center text-xs text-stone-400">
		Already have an account?
		<a href="/auth/login" class="font-medium text-green-700 transition-colors hover:text-green-900"
			>Sign in →</a
		>
	</p>
</div>
