// frontend/app/page.tsx
import NewsComponent from '@/components/NewsComponent';
import MacroComponent from '@/components/macro/MacroComponent';
import StockDashboard from '@/components/stock/StockDashboard';

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-slate-50 dark:bg-slate-950">
      <div className="max-w-7xl mx-auto space-y-8">
        <header>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            📊 Finance Dashboard
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            AI-powered market insights and economic analysis
          </p>
        </header>

        <section>
          <NewsComponent />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <section>
              <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-slate-200">Single Stock Analysis</h2>
              <StockDashboard />
            </section>

            <section>
                <h2 className="text-xl font-semibold mb-4 text-slate-800 dark:text-slate-200">Macro Economic Data</h2>
                <MacroComponent />
            </section>
        </div>
      </div>
    </main>
  );
}
