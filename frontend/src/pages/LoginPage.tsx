import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../lib/apiClient';
import { setAuthToken, setUser } from '../lib/auth';
import { getErrorMessage } from '../lib/error';
import { Cpu, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function LoginPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setErrorMessage('');

        try {
            const response = await apiClient.post('/auth/login', {
                email,
                password,
            });

            setAuthToken(response.data);

            // Fetch user info
            const userResponse = await apiClient.get('/auth/me');
            setUser(userResponse.data);

            toast.success('Login successful');
            navigate('/dashboard');
        } catch (error: any) {
            const message = getErrorMessage(error, 'Login failed');
            setErrorMessage(message);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-shell">
            <div className="w-full max-w-md">
                <div className="flex items-center justify-center gap-3 mb-8">
                    <div className="h-12 w-12 rounded-2xl bg-[var(--primary)] text-white flex items-center justify-center shadow-lg shadow-blue-900/20">
                        <Cpu className="w-6 h-6" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold">PCBuilder</h1>
                        <p className="text-sm text-[color:var(--text-soft)]">Build with confidence</p>
                    </div>
                </div>

                <div className="soft-card auth-card">
                    <h2 className="text-2xl font-bold mb-2">Welcome back</h2>
                    <p className="text-sm text-[color:var(--text-soft)] mb-7">Sign in to your account to continue.</p>

                    {errorMessage ? (
                        <div className="mb-5 rounded-xl border border-[color:var(--danger)]/30 bg-[color:var(--danger)]/10 px-4 py-3 text-sm text-[color:var(--danger)] whitespace-pre-line">
                            {errorMessage}
                        </div>
                    ) : null}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-semibold mb-2 text-[color:var(--text-main)]">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                disabled={loading}
                                placeholder="you@example.com"
                                className="input-premium disabled:opacity-50"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold mb-2 text-[color:var(--text-main)]">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                disabled={loading}
                                placeholder="••••••••"
                                className="input-premium disabled:opacity-50"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full min-h-11 btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign in'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-[color:var(--text-soft)]">Don't have an account?{' '}
                            <Link to="/register" className="font-semibold text-[color:var(--primary)] hover:text-[color:var(--primary-strong)]">Register here</Link>
                        </p>
                    </div>
                </div>

                <div className="mt-6 p-4 muted-panel text-center text-sm text-[color:var(--text-soft)]">
                    Demo: Use admin credentials or create a new account
                </div>
            </div>
        </div>
    );
}
