import Layout from '../components/Layout';

export default function DashboardPage() {
    return (
        <Layout>
            <div className="mb-8">
                <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-5 mb-8">
                    <div>
                        <h1 className="text-4xl font-bold">Dashboard</h1>
                        <p className="text-sm text-[color:var(--text-soft)] mt-2">Public builds feed is coming soon.</p>
                    </div>
                </div>

                <div className="soft-card p-10 text-center">
                    <h2 className="text-2xl font-semibold mb-3">Community Builds Feed</h2>
                    <p className="text-[color:var(--text-soft)] max-w-2xl mx-auto">
                        This page will show public builds shared by users, including ratings and reviews.
                        For now, manage your own builds in the Builder page.
                    </p>
                </div>
            </div>
        </Layout>
    );
}
