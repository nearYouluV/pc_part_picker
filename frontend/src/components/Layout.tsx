import type { ReactNode } from 'react';
import TopNav from './TopNav';

interface LayoutProps {
    children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    return (
        <div className="app-shell animate-page-fade">
            <div className="app-container">
                <TopNav />
                <main className="flex-1 overflow-auto">
                    <div className="content-wrap">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
