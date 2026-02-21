<script lang="ts">
  import './layout.css';
  import favicon from '$lib/assets/favicon.svg';
  import { page } from '$app/stores';

  let { children } = $props();

  let isMapPage = $derived($page.url.pathname === '/map');
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<!-- Header -->
<nav class="fixed inset-x-0 top-0 z-50 h-14 bg-stone-50/90 backdrop-blur-md border-b border-stone-200 flex items-center justify-between px-8">
  <a href="/" class="flex items-center gap-2.5">
    <div class="w-7 h-7 rounded-lg bg-green-900 flex items-center justify-center">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="white">
        <path d="M17 7c0-1.1-.9-2-2-2H9C7.9 5 7 5.9 7 7v1h10V7zm0 2H7v9h10V9zm-5 7a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"/>
      </svg>
    </div>
    <span class="font-serif font-semibold text-stone-800 text-[15px] tracking-tight">Snap Species</span>
  </a>

  <div class="flex items-center gap-0.5">
    <a href="/scan"  class="text-sm text-stone-500 hover:text-stone-800 hover:bg-stone-100 px-3.5 py-1.5 rounded-md transition-colors">Scan</a>
    <a href="/map"   class="text-sm text-stone-500 hover:text-stone-800 hover:bg-stone-100 px-3.5 py-1.5 rounded-md transition-colors">Map</a>
    <a href="/about" class="text-sm text-stone-500 hover:text-stone-800 hover:bg-stone-100 px-3.5 py-1.5 rounded-md transition-colors">About</a>
  </div>

  <a href="/scan" class="text-sm font-medium bg-green-900 text-white px-4 py-2 rounded-lg hover:bg-green-950 transition-colors">
    Start scanning →
  </a>
</nav>

<!-- Main content — pt-14 offsets the fixed nav -->
<main class="{isMapPage ? 'h-[calc(100vh-3.5rem)] pt-14 overflow-hidden' : 'pt-14'}">
  {@render children()}
</main>

<!-- Footer — hidden on map page -->
{#if !isMapPage}
  <footer class="max-w-5xl mx-auto px-8 py-7 border-t border-stone-200 flex items-center justify-between">
    <div class="flex items-center gap-5">
      <div class="flex items-center gap-2">
        <div class="w-6 h-6 rounded-md bg-green-900 flex items-center justify-center">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="white">
            <path d="M17 7c0-1.1-.9-2-2-2H9C7.9 5 7 5.9 7 7v1h10V7zm0 2H7v9h10V9zm-5 7a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"/>
          </svg>
        </div>
        <span class="font-serif font-semibold text-stone-700 text-sm">Snap Species</span>
      </div>
      <span class="text-xs font-mono text-stone-400">Built for wildlife conservation.</span>
    </div>
    <div class="flex gap-6">
      <a href="/scan"  class="text-xs font-mono text-stone-400 hover:text-stone-600 transition-colors">Scan</a>
      <a href="/map"   class="text-xs font-mono text-stone-400 hover:text-stone-600 transition-colors">Map</a>
      <a href="/about" class="text-xs font-mono text-stone-400 hover:text-stone-600 transition-colors">About</a>
    </div>
  </footer>
{/if}