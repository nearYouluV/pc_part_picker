export interface User {
    id: number;
    username: string;
    email: string;
    is_active: boolean;
    is_superuser: boolean;
}

export interface AuthToken {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export const setAuthToken = (token: AuthToken) => {
    localStorage.setItem('access_token', token.access_token);
    localStorage.setItem('refresh_token', token.refresh_token);
    localStorage.setItem('token_type', token.token_type);
};

export const setUser = (user: User) => {
    localStorage.setItem('user', JSON.stringify(user));
};

export const getUser = (): User | null => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
};

export const getAccessToken = (): string | null => {
    return localStorage.getItem('access_token');
};

export const isLoggedIn = (): boolean => {
    return !!getAccessToken();
};

export const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user');
};
