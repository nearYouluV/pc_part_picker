import Layout from '../components/Layout';
import ScrapingPanel from '../components/ScrapingPanel';

export default function ScrapingPage() {
    const categories = ['CPU', 'GPU', 'RAM', 'SSD', 'HDD', 'Motherboard', 'PSU', 'Air Cooling', 'Water Cooling'];

    return (
        <Layout>
            <div className="mb-8">
                <h1 className="text-4xl font-bold">Scraping Panel</h1>
                <p className="text-sm text-[color:var(--text-soft)] mt-2">Trigger product scraping tasks to populate the component database.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <ScrapingPanel />

                <div className="space-y-4">
                    <div className="soft-card p-6">
                        <h3 className="text-lg font-semibold mb-4">How it works</h3>
                        <ul className="space-y-3 text-sm text-[color:var(--text-soft)]">
                            <li className="flex gap-3">
                                <span className="font-semibold text-[color:var(--primary)]">1.</span>
                                <span>Select a component category (CPU, GPU, RAM, etc.)</span>
                            </li>
                            <li className="flex gap-3">
                                <span className="font-semibold text-[color:var(--primary)]">2.</span>
                                <span>Click "Trigger Scraping" to start the task</span>
                            </li>
                            <li className="flex gap-3">
                                <span className="font-semibold text-[color:var(--primary)]">3.</span>
                                <span>Products are fetched and added to the database</span>
                            </li>
                            <li className="flex gap-3">
                                <span className="font-semibold text-[color:var(--primary)]">4.</span>
                                <span>Use new products in the Builder component selector</span>
                            </li>
                        </ul>
                    </div>

                    <div className="soft-card p-6">
                        <h3 className="text-lg font-semibold mb-3">Supported Categories</h3>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-sm">
                            {categories.map((category) => (
                                <span key={category} className="tag-chip">
                                    {category}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
