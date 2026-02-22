<script lang="ts">
  import type { User, Sighting, LeaderboardEntry } from '$lib/types';

  //Todo: Replace with real data
  const user: User = {
    username: 'jane_doe',
    email: 'jane@example.com',
  };

  const entry: LeaderboardEntry = {
    rank: 2,
    name: 'Jane Doe',
    score: 13_405,
    species: 47,
    joined: '2023-04-12',
  };

  const sightings: Sighting[] = [
    { id: 1,  name: 'Amur Leopard',       sci: 'Panthera pardus orientalis',  status: 'CR', lat: 43.1,  lng: 131.9, timestamp: 1719000000, threat_score: 98, reporter: 'jane_doe' },
    { id: 2,  name: 'Snow Leopard',        sci: 'Panthera uncia',              status: 'VU', lat: 27.9,  lng: 86.9,  timestamp: 1718800000, threat_score: 74, reporter: 'jane_doe' },
    { id: 3,  name: 'Sumatran Orangutan',  sci: 'Pongo abelii',                status: 'CR', lat: 3.6,   lng: 98.5,  timestamp: 1718600000, threat_score: 95, reporter: 'jane_doe' },
    { id: 4,  name: 'Clouded Leopard',     sci: 'Neofelis nebulosa',           status: 'VU', lat: 27.5,  lng: 89.6,  timestamp: 1718400000, threat_score: 70, reporter: 'jane_doe' },
    { id: 5,  name: 'Saola',               sci: 'Pseudoryx nghetinhensis',     status: 'CR', lat: 17.4,  lng: 106.2, timestamp: 1718200000, threat_score: 99, reporter: 'jane_doe' },
  ];

  const crCount    = sightings.filter(s => s.status === 'CR').length;
  const avgThreat  = Math.round(sightings.reduce((a, s) => a + s.threat_score, 0) / sightings.length);
  const joinedDate = new Date(entry.joined).toLocaleDateString('en-US', { year: 'numeric', month: 'long' });

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

  const rankLabel = (r: number) =>
    r === 1 ? '1st' : r === 2 ? '2nd' : r === 3 ? '3rd' : `${r}th`;
</script>

<div class="min-h-screen bg-stone-50">
  <div class="mx-auto max-w-5xl px-8 py-16">

    <!-- ── Profile header ── -->
    <div class="mb-12 flex items-start justify-between gap-8">
      <div class="flex items-center gap-6">
        <!-- Avatar -->
        <div class="relative">
          <div class="w-20 h-20 rounded-2xl bg-green-900 flex items-center justify-center shadow-lg shadow-green-900/20">
            <span class="font-serif text-3xl font-semibold text-white">
              {entry.name[0]}
            </span>
          </div>
          <!-- Rank badge -->
          <div class="absolute -bottom-2 -right-2 font-mono text-xs font-bold bg-amber-400 text-amber-900
                      w-7 h-7 rounded-full flex items-center justify-center shadow-sm">
            #{entry.rank}
          </div>
        </div>

        <div>
          <p class="font-mono text-xs tracking-widest text-green-700 uppercase mb-1">Observer</p>
          <h1 class="font-serif text-3xl font-semibold text-stone-900 leading-none">{entry.name}</h1>
          <p class="font-mono text-sm text-stone-400 mt-1.5">@{user.username}</p>
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
        { label: 'Conservation score', value: entry.score.toLocaleString(), sub: `Rank ${rankLabel(entry.rank)} globally` },
        { label: 'Species documented', value: entry.species,               sub: `${crCount} critically endangered` },
        { label: 'Avg threat score',   value: `${avgThreat}%`,             sub: 'Weighted by IUCN status' },
        { label: 'Member since',       value: joinedDate,                   sub: `${sightings.length} total sightings` },
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
        </div>
      </div>

      <!-- Right col — account info + standing -->
      <div class="col-span-1 flex flex-col gap-6">

        <!-- Account details -->
        <div class="rounded-2xl border border-stone-200 overflow-hidden">
          <div class="px-6 py-5 border-b border-stone-100">
            <p class="font-mono text-xs tracking-widest text-stone-400 uppercase">Account</p>
          </div>
          <div class="divide-y divide-stone-100">
            {#each [
              { label: 'Username', value: `@${user.username}` },
              { label: 'Email',    value: user.email           },
            ] as row}
              <div class="px-6 py-4">
                <p class="font-mono text-xs text-stone-400 uppercase tracking-widest mb-1">{row.label}</p>
                <p class="font-serif text-sm font-medium text-stone-800 truncate">{row.value}</p>
              </div>
            {/each}
          </div>
          <div class="px-6 py-4 border-t border-stone-100">
            <a
              href="/auth/logout"
              class="font-mono text-xs text-red-400 hover:text-red-600 transition-colors"
            >
              Sign out →
            </a>
          </div>
        </div>

        <!-- Global standing -->
        <div class="rounded-2xl border border-stone-200 overflow-hidden">
          <div class="px-6 py-5 border-b border-stone-100">
            <p class="font-mono text-xs tracking-widest text-stone-400 uppercase">Global standing</p>
          </div>
          <div class="px-6 py-6 flex flex-col gap-5">
            <!-- Rank visual -->
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center flex-shrink-0">
                <span class="font-mono text-lg font-bold text-amber-500">#{entry.rank}</span>
              </div>
              <div>
                <p class="font-serif text-sm font-semibold text-stone-800">{rankLabel(entry.rank)} place</p>
                <p class="font-mono text-xs text-stone-400">out of 12,483 observers</p>
              </div>
            </div>

            <!-- Score bar — top 1% visual -->
            <div>
              <div class="flex justify-between mb-2">
                <span class="font-mono text-xs text-stone-400">Your score</span>
                <span class="font-mono text-xs text-green-700 font-medium">Top {Math.ceil((entry.rank / 12483) * 100)}%</span>
              </div>
              <div class="h-2 w-full rounded-full bg-stone-100 overflow-hidden">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-green-600 to-green-400"
                  style="width: {Math.max(4, 100 - (entry.rank / 12483) * 100)}%"
                ></div>
              </div>
            </div>

            <!-- Species breakdown -->
            <div class="grid grid-cols-3 gap-2 pt-1">
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
</div>