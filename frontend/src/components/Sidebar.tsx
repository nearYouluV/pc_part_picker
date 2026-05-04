import { useNavigate, useLocation } from 'react-router-dom';
import { Cpu, LogOut, Home, Zap } from 'lucide-react';
import { logout } from '../lib/auth';

export default function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isActive = (path: string) => location.pathname === path;

    const linkClasses = (path: string) =>
        `flex items-center gap-3 px-4 py-2 rounded-xl transition-all ${isActive(path)
            ? 'bg-muted/10 text-foreground shadow-sm'
            : 'text-muted-foreground hover:bg-muted/20 hover:text-foreground'
        }`;

    return (
        <aside className="w-64 bg-card border-r border-border p-6 flex flex-col gap-6">
            {/* Logo */}
            <div className="flex items-center gap-3 mb-4">
                <Cpu className="w-6 h-6 text-muted-foreground" />
                <h1 className="text-lg font-semibold text-foreground">PCBuilder</h1>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-2">
                <button
                    onClick={() => navigate('/dashboard')}
                    className={linkClasses('/dashboard')}
                >
                    <Home className="w-5 h-5" />
                    <span>Dashboard</span>
                </button>

                <button
                    onClick={() => navigate('/builder')}
                    className={linkClasses('/builder')}
                >
                    <Cpu className="w-5 h-5" />
                    <span>Builder</span>
                </button>

                <button
                    onClick={() => navigate('/scraping')}
                    className={linkClasses('/scraping')}
                >
                    <Zap className="w-5 h-5" />
                    <span>Scraping</span>
                </button>
            </nav>

            {/* Logout */}
            <button
                onClick={handleLogout}
                className="flex items-center gap-3 px-4 py-2 rounded-xl text-destructive hover:bg-destructive/10 transition w-full"
            >
                <LogOut className="w-5 h-5" />
                <span>Logout</span>
            </button>
        </aside>
    );
}
