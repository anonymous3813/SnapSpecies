import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { isLoggedIn } from '$lib/stores/authStore.svelte';

export const load: PageLoad = async () => {
    if (isLoggedIn() === false) {
        throw redirect(303, '/auth/login');
    }
};
