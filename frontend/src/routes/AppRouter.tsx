import type { ReactNode } from 'react';
import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
    useLocation,
} from 'react-router-dom';
import { isAdmin, isLoggedIn } from '../lib/auth';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import DashboardPage from '../pages/DashboardPage';
import BuilderPage from '../pages/BuilderPage';
import AIChatPage from '../pages/AIChatPage';
import ScrapingPage from '../pages/ScrapingPage';
import ProductPage from '../pages/ProductPage';
import ProductsPage from '../pages/ProductsPage';
import PublicBuildPage from '../pages/PublicBuildPage';

interface ProtectedRouteProps {
    children: ReactNode;
}

interface AdminRouteProps {
    children: ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
    const location = useLocation();

    if (!isLoggedIn()) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
}

function AdminRoute({ children }: AdminRouteProps) {
    const location = useLocation();

    if (!isLoggedIn()) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (!isAdmin()) {
        return <Navigate to="/dashboard" replace />;
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
                    path="/ai-chat"
                    element={
                        <ProtectedRoute>
                            <AIChatPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/scraping"
                    element={
                        <AdminRoute>
                            <ScrapingPage />
                        </AdminRoute>
                    }
                />
                <Route
                    path="/product/:id"
                    element={
                        <ProtectedRoute>
                            <ProductPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/products"
                    element={
                        <ProtectedRoute>
                            <ProductsPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/community/builds/:id"
                    element={
                        <ProtectedRoute>
                            <PublicBuildPage />
                        </ProtectedRoute>
                    }
                />

                {/* Redirect */}
                <Route
                    path="/"
                    element={
                        isLoggedIn() ? (
                            <Navigate to="/builder" replace />
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
