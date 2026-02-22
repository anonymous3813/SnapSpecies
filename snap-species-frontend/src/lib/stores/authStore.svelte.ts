import type { User } from '$lib/types';

export const authStore = $state({
	user: null as User | null
});

export const isLoggedIn = () => authStore.user !== null;

export const logOut = () => {
	authStore.user = null;
};

export const logIn = (user: User) => {
	authStore.user = user;
};
