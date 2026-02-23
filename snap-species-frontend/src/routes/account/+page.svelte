<script lang="ts">
  import type { User, Sighting } from '$lib/types';

  let { data } = $props();

  const user = $derived((data?.user ?? { username: '', name: '', email: '' }) as User & { name?: string });
  const stats = $derived(data?.stats ?? null);
  const sightings = $derived(Array.isArray(data?.sightings) ? data.sightings : []) as Sighting[];

  const displayName = $derived(user.name || user.email || user.username || 'Observer');
  const crCount = $derived(sightings.filter(s => s.status === 'CR').length);
  const avgThreat = $derived(sightings.length ? Math.round(sightings.reduce((a, s) => a + s.threat_score, 0) / sightings.length) : (stats?.avg_threat_score ?? 0));
  const score = $derived(stats ? Math.round((stats.total_sightings || 0) * (stats.avg_threat_score || 0)) : 0);

  const STATUS_META: Record<string, { label: string; bg: string; text: string }> = {
    CR: { label: 'CR', bg: 'bg-red-50',    text: 'text-red-500'    },
    EN: { label: 'EN', bg: 'bg-orange-50', text: 'text-orange-500' },
    VU: { label: 'VU', bg: 'bg-amber-50',  text: 'text-amber-600'  },
    NT: { label: 'NT', bg: 'bg-blue-50',   text: 'text-blue-400'   },
    LC: { label: 'LC', bg: 'bg-green-50',  text: 'text-green-600'  },
  };

  function formatTimestamp(ts: number) {
    return new Date(ts * 1000).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric'
    });
  }

  function coords(s: Sighting) {
    const lat = s.lat >= 0 ? `${s.lat}°N` : `${Math.abs(s.lat)}°S`;
    const lng = s.lng >= 0 ? `${s.lng}°E` : `${Math.abs(s.lng)}°W`;
    return `${lat}, ${lng}`;
  }

</script>

<div class="min-h-screen bg-stone-50">
  <div class="mx-auto max-w-5xl px-8 py-16">

    <!-- ── Profile header ── -->
    <div class="mb-12 flex items-start justify-between gap-8">
      <div class="flex items-center gap-6">
        <div class="w-20 h-20 rounded-2xl bg-green-900 flex items-center justify-center shadow-lg shadow-green-900/20">
          <span class="font-serif text-3xl font-semibold text-white">
            {(displayName[0] || '?').toUpperCase()}
          </span>
        </div>
        <div>
          <p class="font-mono text-xs tracking-widest text-green-700 uppercase mb-1">Observer</p>
          <h1 class="font-serif text-3xl font-semibold text-stone-900 leading-none">{displayName}</h1>
          <p class="font-mono text-sm text-stone-400 mt-1.5">{user.email || user.username}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3 mt-1">
        <a
          href="/account/edit"
          class="text-sm font-medium text-stone-600 border border-stone-200 bg-white px-4 py-2.5 rounded-xl
                 hover:border-stone-300 hover:bg-stone-50 transition-all"
        >
          Edit profile
        </a>
        <a
          href="/scan"
          class="text-sm font-medium bg-green-900 text-white px-4 py-2.5 rounded-xl
                 hover:bg-green-950 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-green-900/20
                 flex items-center gap-1.5"
        >
          Add sighting <span class="text-green-400">→</span>
        </a>
      </div>
    </div>

    <!-- ── Stats grid ── -->
    <div class="grid grid-cols-4 gap-px overflow-hidden rounded-2xl border border-stone-200 bg-stone-200 mb-8">
      {#each [
        { label: 'Conservation score', value: score.toLocaleString(), sub: 'From your sightings' },
        { label: 'Total sightings', value: stats?.total_sightings ?? sightings.length, sub: `${crCount} critically endangered` },
        { label: 'Avg threat score', value: `${Math.round(stats?.avg_threat_score ?? avgThreat)}`, sub: 'Weighted by IUCN status' },
        { label: 'Species documented', value: stats?.total_sightings ?? sightings.length, sub: `${sightings.length} on map` },
      ] as stat}
        <div class="bg-white px-6 py-6">
          <p class="font-mono text-xs tracking-widest text-stone-400 uppercase mb-3">{stat.label}</p>
          <p class="font-serif text-2xl font-semibold text-stone-900 leading-none mb-1">{stat.value}</p>
          <p class="font-mono text-xs text-stone-400">{stat.sub}</p>
        </div>
      {/each}
    </div>

    <!-- ── Two-col lower ── -->
    <div class="grid grid-cols-3 gap-6">

      <!-- Sightings table — 2/3 width -->
      <div class="col-span-2 rounded-2xl border border-stone-200 overflow-hidden">
        <div class="px-7 py-5 border-b border-stone-100 flex items-center justify-between">
          <p class="font-mono text-xs tracking-widest text-stone-400 uppercase">My sightings</p>
          <a href="/sightings" class="font-mono text-xs text-green-700 hover:text-green-900 transition-colors">
            View all →
          </a>
        </div>

        <div class="divide-y divide-stone-100">
          {#if sightings.length === 0}
            <div class="px-7 py-10 text-center">
              <p class="font-mono text-sm text-stone-500 mb-2">No sightings yet</p>
              <p class="text-xs text-stone-400 mb-4">Add a sighting from the scan page to see it here.</p>
              <a href="/scan" class="inline-flex items-center gap-1.5 rounded-xl bg-green-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-green-950 transition-colors">Add sighting →</a>
            </div>
          {:else}
          {#each sightings as s}
            {@const meta = STATUS_META[s.status]}
            <div class="flex items-center gap-4 px-7 py-4 hover:bg-stone-50 transition-colors group">
              <!-- Status -->
              <span class="flex-shrink-0 font-mono text-xs font-semibold px-1.5 py-0.5 rounded {meta.bg} {meta.text}">
                {meta.label}
              </span>
              <!-- Species -->
              <div class="flex-1 min-w-0">
                <div class="font-serif text-sm font-semibold text-stone-800 leading-snug truncate">{s.name}</div>
                <div class="font-mono text-xs text-stone-400 italic truncate">{s.sci}</div>
              </div>
              <!-- Threat score bar -->
              <div class="w-16 flex-shrink-0">
                <div class="flex items-center justify-between mb-1">
                  <span class="font-mono text-xs text-stone-400">{s.threat_score}</span>
                </div>
                <div class="h-1 w-full rounded-full bg-stone-100 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all
                           {s.threat_score >= 90 ? 'bg-red-400' :
                            s.threat_score >= 70 ? 'bg-amber-400' : 'bg-green-500'}"
                    style="width: {s.threat_score}%"
                  ></div>
                </div>
              </div>
              <!-- Coords + date -->
              <div class="text-right flex-shrink-0 hidden xl:block">
                <div class="font-mono text-xs text-stone-500">{coords(s)}</div>
                <div class="font-mono text-xs text-stone-300">{formatTimestamp(s.timestamp)}</div>
              </div>
            </div>
          {/each}
          {/if}
        </div>
      </div>

      <!-- Right col — account info -->
      <div class="col-span-1 flex flex-col gap-6">

        <!-- Account details -->
        <div class="rounded-2xl border border-stone-200 overflow-hidden">
          <div class="px-6 py-5 border-b border-stone-100">
            <p class="font-mono text-xs tracking-widest text-stone-400 uppercase">Account</p>
          </div>
          <div class="divide-y divide-stone-100">
            {#each [
              { label: 'Name', value: displayName },
              { label: 'Email', value: user.email || user.username },
            ] as row}
              <div class="px-6 py-4">
                <p class="font-mono text-xs text-stone-400 uppercase tracking-widest mb-1">{row.label}</p>
                <p class="font-serif text-sm font-medium text-stone-800 truncate">{row.value}</p>
              </div>
            {/each}
          </div>
          <div class="px-6 py-4 border-t border-stone-100">
            <form method="POST" action="/auth/logout">
              <button type="submit" class="font-mono text-xs text-red-400 hover:text-red-600 transition-colors">
                Sign out →
              </button>
            </form>
          </div>
        </div>

        <div class="rounded-2xl border border-stone-200 overflow-hidden">
          <div class="px-6 py-5 border-b border-stone-100">
            <p class="font-mono text-xs tracking-widest text-stone-400 uppercase">Endangered breakdown</p>
          </div>
          <div class="px-6 py-6 grid grid-cols-3 gap-2">
            {#each [
              { status: 'CR', count: crCount,                                          bg: 'bg-red-50',    text: 'text-red-500'    },
              { status: 'EN', count: sightings.filter(s => s.status === 'EN').length,  bg: 'bg-orange-50', text: 'text-orange-500' },
              { status: 'VU', count: sightings.filter(s => s.status === 'VU').length,  bg: 'bg-amber-50',  text: 'text-amber-600'  },
            ] as b}
              <div class="rounded-xl {b.bg} px-3 py-2.5 text-center">
                <p class="font-mono text-xs font-semibold {b.text}">{b.status}</p>
                <p class="font-serif text-lg font-semibold {b.text}">{b.count}</p>
              </div>
            {/each}
          </div>
        </div>

      </div>
    </div>

  </div>
</div>