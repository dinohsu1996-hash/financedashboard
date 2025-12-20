// frontend/components/macro/MacroComponent.tsx
"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { fetchMacroData, synthesizeMacro } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Loader2, Activity, BrainCircuit } from 'lucide-react';

const INDICATOR_GROUPS = {
  "1. Leading Economic Indicators (Future Trends)": [
    { label: "Average Weekly Hours (Manufacturing)", seriesId: "AWHMAN", unit: "Hours" },
    { label: "Initial Jobless Claims", seriesId: "ICSA", unit: "Thousands" },
    { label: "Manufacturers' New Orders", seriesId: "AMDMNO-US", unit: "Millions USD" },
    { label: "Vendor Performance Index (ISM)", seriesId: "PMICD", unit: "Index" },
    { label: "Non-Defense Capital Goods Orders", seriesId: "NEWORDER", unit: "Millions USD" },
    { label: "Building Permits (New Housing)", seriesId: "PERMIT", unit: "Units" },
    { label: "S&P 500 Index (Stock Prices)", seriesId: "SP500", unit: "Index" },
    { label: "Consumer Expectations", seriesId: "UMCSENT", unit: "Index" },
    { label: "Personal Consumption Expenditures", seriesId: "PCE", unit: "Billions USD" },
  ],
  "2. Monetary & Inflation (Policy Focus)": [
    { label: "Federal Funds Rate (Current)", seriesId: "FEDFUNDS", unit: "Percent" },
    { label: "10-Year Treasury Yield", seriesId: "DGS10", unit: "Percent" },
    { label: "US Core Inflation (CPI)", seriesId: "CPILFESL", unit: "Index" },
    { label: "Inflation, consumer prices for the United States", seriesId: "FPCPITOTLZGUSA", unit: "Percent" },
    { label: "M2 Money Supply", seriesId: "M2SL", unit: "Billions USD" },
  ],
  "3. Lagging Indicators (Past Confirmation)": [
    { label: "Unemployment Rate", seriesId: "UNRATE", unit: "Percent" }
  ]
};

export default function MacroComponent() {
  const groupKeys = Object.keys(INDICATOR_GROUPS);
  const [selectedGroup, setSelectedGroup] = useState<string>(groupKeys[0]);
  const [selectedIndicator, setSelectedIndicator] = useState(INDICATOR_GROUPS[groupKeys[0] as keyof typeof INDICATOR_GROUPS][0]);
  const [years, setYears] = useState<number>(5);
  const [analysisFocus, setAnalysisFocus] = useState<string>("Impact of inflation and interest rates on recession risk");

  const [chartData, setChartData] = useState<any[]>([]);
  const [loadingChart, setLoadingChart] = useState<boolean>(false);
  const [chartError, setChartError] = useState<string | null>(null);

  const [synthesis, setSynthesis] = useState<string | null>(null);
  const [loadingSynthesis, setLoadingSynthesis] = useState<boolean>(false);

  // Update selected indicator when group changes
  useEffect(() => {
    const group = INDICATOR_GROUPS[selectedGroup as keyof typeof INDICATOR_GROUPS];
    if (group && group.length > 0) {
      setSelectedIndicator(group[0]);
    }
  }, [selectedGroup]);

  // Fetch chart data when indicator or years change
  useEffect(() => {
    async function loadData() {
      setLoadingChart(true);
      setChartError(null);
      try {
        const data = await fetchMacroData(selectedIndicator.seriesId, selectedIndicator.label, years);
        setChartData(data);
      } catch (err: any) {
        setChartError("Failed to fetch data for " + selectedIndicator.label);
        setChartData([]);
      } finally {
        setLoadingChart(false);
      }
    }
    loadData();
  }, [selectedIndicator, years]);

  const handleSynthesize = async () => {
    setLoadingSynthesis(true);
    try {
      // Prepare data for backend: Dict[str, List[List[str]]]
      const groupedForBackend: any = {};
      for (const [group, indicators] of Object.entries(INDICATOR_GROUPS)) {
        groupedForBackend[group] = indicators.map(ind => [ind.label, ind.seriesId, ind.unit]);
      }

      const result = await synthesizeMacro(groupedForBackend, analysisFocus);
      setSynthesis(result.conclusion);
    } catch (err: any) {
      setSynthesis("Error generating synthesis: " + err.message);
    } finally {
      setLoadingSynthesis(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-6 w-6" />
            Macroeconomic Indicators (FRED Data)
          </CardTitle>
          <CardDescription>Explore economic trends and generate AI insights</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Left Column: Controls */}
            <div className="lg:col-span-1 space-y-6">

              {/* Group Selection */}
              <div>
                <h4 className="font-semibold mb-2">Indicator Group</h4>
                <div className="space-y-2">
                  {groupKeys.map(group => (
                    <div key={group} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="group"
                        id={group}
                        checked={selectedGroup === group}
                        onChange={() => setSelectedGroup(group)}
                        className="h-4 w-4 text-blue-600"
                      />
                      <label htmlFor={group} className="text-sm cursor-pointer select-none">{group}</label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Indicator Selection */}
              <div>
                 <h4 className="font-semibold mb-2">Choose Indicator</h4>
                 <select
                    className="w-full p-2 border rounded-md text-sm bg-slate-50 dark:bg-slate-900"
                    value={selectedIndicator.seriesId}
                    onChange={(e) => {
                        const ind = INDICATOR_GROUPS[selectedGroup as keyof typeof INDICATOR_GROUPS].find(i => i.seriesId === e.target.value);
                        if (ind) setSelectedIndicator(ind);
                    }}
                 >
                    {INDICATOR_GROUPS[selectedGroup as keyof typeof INDICATOR_GROUPS].map(ind => (
                        <option key={ind.seriesId} value={ind.seriesId}>{ind.label}</option>
                    ))}
                 </select>
              </div>

              {/* Years Slider */}
              <div>
                 <h4 className="font-semibold mb-2">History: {years} Years</h4>
                 <input
                   type="range"
                   min="1"
                   max="50"
                   value={years}
                   onChange={(e) => setYears(parseInt(e.target.value))}
                   className="w-full"
                 />
              </div>

              {/* Analysis Focus */}
              <div>
                  <h4 className="font-semibold mb-2">AI Analysis Focus</h4>
                  <input
                    type="text"
                    value={analysisFocus}
                    onChange={(e) => setAnalysisFocus(e.target.value)}
                    className="w-full p-2 border rounded-md text-sm bg-slate-50 dark:bg-slate-900"
                  />
              </div>

              {/* Synthesize Button */}
              <button
                  onClick={handleSynthesize}
                  disabled={loadingSynthesis}
                  className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loadingSynthesis ? <Loader2 className="h-4 w-4 animate-spin" /> : <BrainCircuit className="h-4 w-4" />}
                  {loadingSynthesis ? 'Analyzing...' : 'Synthesize Conclusion'}
              </button>

            </div>

            {/* Right Column: Chart & Synthesis */}
            <div className="lg:col-span-2 space-y-6">

              {/* Chart */}
              <div className="bg-white dark:bg-slate-950 p-4 rounded-lg border h-[400px]">
                <h3 className="text-lg font-medium mb-4 text-center">{selectedIndicator.label} ({selectedIndicator.unit})</h3>
                {loadingChart ? (
                   <div className="h-full flex items-center justify-center text-slate-400">Loading chart data...</div>
                ) : chartError ? (
                   <div className="h-full flex items-center justify-center text-red-400">{chartError}</div>
                ) : chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="90%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis
                        dataKey="Date"
                        tickFormatter={(value) => new Date(value).getFullYear().toString()}
                        minTickGap={50}
                        tick={{fontSize: 12}}
                      />
                      <YAxis domain={['auto', 'auto']} tick={{fontSize: 12}} />
                      <Tooltip
                        contentStyle={{backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: '8px'}}
                        labelStyle={{color: '#666'}}
                      />
                      <Line type="monotone" dataKey="Value" stroke="#2563eb" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-400">No data available</div>
                )}
              </div>

              {/* Synthesis Result */}
              {synthesis && (
                <div className="bg-blue-50 dark:bg-blue-950/30 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
                    <h3 className="text-lg font-bold text-blue-800 dark:text-blue-300 mb-2 flex items-center gap-2">
                        <BrainCircuit className="h-5 w-5" />
                        Economic Synthesis & Outlook
                    </h3>
                    <div className="prose prose-sm dark:prose-invert max-w-none text-slate-700 dark:text-slate-300">
                        <div dangerouslySetInnerHTML={{ __html: synthesis.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br/>') }} />
                    </div>
                </div>
              )}

            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
