// frontend/components/stock/StockDashboard.tsx
"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { fetchStockOverview, fetchStockHistory, fetchStockFinancials } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Loader2, Search, TrendingUp, DollarSign, PieChart } from 'lucide-react';

export default function StockDashboard() {
  const [ticker, setTicker] = useState<string>("AAPL");
  const [loading, setLoading] = useState<boolean>(false);
  const [overview, setOverview] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [financials, setFinancials] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("overview"); // overview, charts, financials

  const handleSearch = async () => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    setOverview(null);
    setHistory([]);
    setFinancials([]);

    try {
      // Parallel fetch
      const [ovData, histData] = await Promise.all([
        fetchStockOverview(ticker),
        fetchStockHistory(ticker, "1y")
      ]);

      setOverview(ovData);
      setHistory(histData);

      // Fetch financials separately or lazy load? Let's lazy load active tab logic later,
      // but for now maybe just fetch income statement as default.
      try {
          const finData = await fetchStockFinancials(ticker, "income", "yahoo");
          setFinancials(finData);
      } catch (e) {
          console.warn("Financials fetch failed", e);
      }

    } catch (err: any) {
      setError("Failed to fetch stock data. Please check the ticker.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <input
              type="text"
              className="flex-1 p-2 border rounded-md text-lg uppercase font-bold"
              placeholder="Enter Ticker (e.g. MSFT, NVDA)"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="bg-blue-600 text-white px-6 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Search />}
            </button>
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {overview && (
        <div className="space-y-6">

          {/* Header Info */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <h2 className="text-3xl font-bold">{overview.name} ({overview.ticker})</h2>
                <p className="text-slate-500">{overview.sector} • {overview.industry}</p>
            </div>
            <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">
                    ${overview.price?.toFixed(2)}
                </div>
                <div className="text-sm text-slate-500">{overview.currency}</div>
            </div>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <KpiCard label="Market Cap" value={formatNumber(overview.market_cap)} icon={<PieChart className="h-4 w-4 text-purple-500"/>} />
             <KpiCard label="P/E Ratio" value={overview.pe_ratio?.toFixed(2)} icon={<TrendingUp className="h-4 w-4 text-green-500"/>} />
             <KpiCard label="Div Yield" value={(overview.dividend_yield * 100)?.toFixed(2) + "%"} icon={<DollarSign className="h-4 w-4 text-yellow-500"/>} />
             <KpiCard label="52W High" value={overview.fifty_two_week_high?.toFixed(2)} />
          </div>

          {/* Tabs */}
          <div className="border-b border-slate-200 dark:border-slate-800">
            <nav className="-mb-px flex space-x-8">
               {['overview', 'charts', 'financials'].map((tab) => (
                 <button
                   key={tab}
                   onClick={() => setActiveTab(tab)}
                   className={`
                     whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize
                     ${activeTab === tab
                       ? 'border-blue-500 text-blue-600'
                       : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
                   `}
                 >
                   {tab}
                 </button>
               ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="min-h-[400px]">
             {activeTab === 'overview' && (
                 <div className="space-y-4">
                     <h3 className="text-lg font-semibold">Business Summary</h3>
                     <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-sm">
                         {overview.description}
                     </p>
                 </div>
             )}

             {activeTab === 'charts' && (
                 <div className="h-[500px] bg-white dark:bg-slate-900 border rounded-lg p-4">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={history}>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                            <XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} minTickGap={30} />
                            <YAxis domain={['auto', 'auto']} />
                            <Tooltip contentStyle={{ borderRadius: '8px' }} />
                            <Line type="monotone" dataKey="close" stroke="#2563eb" dot={false} strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                 </div>
             )}

             {activeTab === 'financials' && (
                 <div className="overflow-x-auto">
                     {financials.length > 0 ? (
                         <table className="w-full text-sm text-left">
                             <thead className="bg-slate-50 dark:bg-slate-900">
                                 <tr>
                                     <th className="p-3 border-b">Metric</th>
                                     {financials.slice(0, 5).map((period: any) => (
                                         <th key={period.date} className="p-3 border-b">{period.date}</th>
                                     ))}
                                 </tr>
                             </thead>
                             <tbody>
                                 {/* Just showing a few key metrics for demo */}
                                 {["Total Revenue", "Net Income", "Operating Income", "Gross Profit"].map((metric) => (
                                     <tr key={metric} className="border-b">
                                         <td className="p-3 font-medium">{metric}</td>
                                         {financials.slice(0, 5).map((period: any) => (
                                             <td key={period.date} className="p-3">
                                                 {formatNumber(period[metric])}
                                             </td>
                                         ))}
                                     </tr>
                                 ))}
                             </tbody>
                         </table>
                     ) : (
                         <div className="text-center p-8 text-slate-500">
                             No financial data available from this source.
                         </div>
                     )}
                 </div>
             )}
          </div>

        </div>
      )}
    </div>
  );
}

function KpiCard({ label, value, icon }: { label: string, value: string | number, icon?: React.ReactNode }) {
    return (
        <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-800">
            <div className="flex justify-between items-start mb-2">
                <div className="text-sm text-slate-500 font-medium">{label}</div>
                {icon}
            </div>
            <div className="text-lg font-bold text-slate-900 dark:text-slate-100">
                {value || "—"}
            </div>
        </div>
    )
}

function formatNumber(num: number) {
    if (!num) return "—";
    if (num >= 1e12) return (num / 1e12).toFixed(2) + "T";
    if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
    return num.toLocaleString();
}
