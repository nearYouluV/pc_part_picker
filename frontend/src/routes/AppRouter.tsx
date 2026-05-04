import type { ReactNode } from 'react';
import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
    useLocation,
} from 'react-router-dom';
import { isLoggedIn } from '../lib/auth';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import DashboardPage from '../pages/DashboardPage';
import BuilderPage from '../pages/BuilderPage';
import ScrapingPage from '../pages/ScrapingPage';

interface ProtectedRouteProps {
    children: ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
    const location = useLocation();

    if (!isLoggedIn()) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
}

export default function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Protected Routes */}
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/builder"
                    element={
                        <ProtectedRoute>
                            <BuilderPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/scraping"
                    element={
                        <ProtectedRoute>
                            <ScrapingPage />
                        </ProtectedRoute>
                    }
                />

                {/* Redirect */}
                <Route
                    path="/"
                    element={
                        isLoggedIn() ? (
                            <Navigate to="/dashboard" replace />
                        ) : (
                            <Navigate to="/login" replace />
                        )
                    }
                />

                {/* 404 */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}
