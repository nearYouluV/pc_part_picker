import { useNavigate, useLocation } from 'react-router-dom';
import { Cpu, Home, Zap, Box, LogOut } from 'lucide-react';
import { getUser, logout } from '../lib/auth';

export default function TopNav() {
    const navigate = useNavigate();
    const location = useLocation();
    const user = getUser();

    const isActive = (path: string) => location.pathname.startsWith(path);

    const navItems = [
        { label: 'Dashboard', path: '/dashboard', icon: Home },
        { label: 'Builder', path: '/builder', icon: Cpu },
        { label: 'Products', path: '/products', icon: Box },
        { label: 'Scraping', path: '/scraping', icon: Zap },
    ];

    return (
        <header className="w-full sticky top-0 z-40 top-nav">
            <div className="py-3.5 top-nav-grid">
                <div className="flex items-center gap-3 cursor-pointer min-w-0" onClick={() => navigate('/dashboard')}>
                    <div className="w-10 h-10 rounded-xl bg-[var(--primary)] text-white flex items-center justify-center shadow-md shadow-blue-900/20">
                        <Cpu className="w-5 h-5" />
                    </div>
                    <div className="min-w-0">
                        <span className="text-lg font-semibold leading-none text-[color:var(--text-main)]">PCBuilder</span>
                        <p className="text-xs text-[color:var(--text-soft)] truncate">Smart PC planning</p>
                    </div>
                </div>

                <nav className="hidden md:flex items-center gap-2 justify-self-center">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <button
                                key={item.path}
                                className={`nav-link ${isActive(item.path) ? 'nav-link-active' : ''}`}
                                onClick={() => navigate(item.path)}
                            >
                                <Icon className="w-4 h-4 inline-block mr-2 align-[-2px]" />
                                {item.label}
                            </button>
                        );
                    })}
                </nav>

                <div className="flex items-center gap-3 justify-self-end">
                    <div className="hidden md:flex flex-col text-right bg-[var(--surface)] px-3 py-1.5 rounded-xl border border-[var(--border-soft)]">
                        <span className="text-sm font-semibold text-[color:var(--text-main)]">{user?.username}</span>
                        <span className="text-xs text-[color:var(--text-soft)]">{user?.email}</span>
                    </div>

                    <button
                        onClick={() => {
                            logout();
                            navigate('/login');
                        }}
                        className="h-10 w-10 inline-flex items-center justify-center icon-btn-danger"
                        title="Logout"
                    >
                        <LogOut className="w-4 h-4" />
                    </button>
                </div>
            </div>

            <div className="md:hidden pb-3">
                <nav className="soft-card p-1.5 flex items-center justify-between gap-1">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <button
                                key={item.path}
                                className={`flex-1 nav-link text-xs ${isActive(item.path) ? 'nav-link-active' : ''}`}
                                onClick={() => navigate(item.path)}
                            >
                                <Icon className="w-4 h-4 inline-block mr-1.5 align-[-2px]" />
                                {item.label}
                            </button>
                        );
                    })}
                </nav>
            </div>
        </header>
    );
}
