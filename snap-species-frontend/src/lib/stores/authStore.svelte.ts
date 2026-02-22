import type { User } from '$lib/types';

export const authStore = $state({
	user: null as User | null,
    token: null as string | null
});

export const isLoggedIn = () => authStore.user !== null && authStore.token !== null;

export const logOut = () => {
	authStore.user = null;
    authStore.token = null;
};

export const logIn = (user: User, token: string) => {
	authStore.user = user;
    authStore.token = token;
};
