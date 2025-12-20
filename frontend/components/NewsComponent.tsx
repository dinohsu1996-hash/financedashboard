// frontend/components/NewsComponent.tsx
"use client";

import React, { useState } from 'react';
import { fetchNewsSummary } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Loader2, Newspaper, ExternalLink } from 'lucide-react';

interface SummaryData {
  [url: string]: string;
}

export default function NewsComponent() {
  const [urls, setUrls] = useState<string>("https://www.cnbc.com/market-insider/\nhttps://finance.yahoo.com/topic/stock-market-news/");
  const [topic, setTopic] = useState<string>("Market Open & Key Movers");
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<SummaryData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const urlList = urls.split('\n').map(u => u.trim()).filter(u => u.length > 0);
      const result = await fetchNewsSummary(urlList, topic);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch news summary");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Newspaper className="h-6 w-6" />
            Daily Market Briefing
          </CardTitle>
          <CardDescription>Configure news sources and focus topic</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">News URLs (one per line)</label>
                <textarea
                  className="w-full p-2 border rounded-md h-32 text-sm bg-slate-50 dark:bg-slate-900"
                  value={urls}
                  onChange={(e) => setUrls(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Focus Topic</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded-md text-sm bg-slate-50 dark:bg-slate-900"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
                <button
                  onClick={handleGenerate}
                  disabled={loading}
                  className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                  {loading ? 'Analyzing...' : 'Generate Briefing'}
                </button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
         <div className="p-4 bg-red-50 text-red-600 rounded-md border border-red-200">
            Error: {error}
         </div>
      )}

      {data && (
        <div className="space-y-2">
          <div className="text-sm text-gray-500 text-right">Last updated: {data.timestamp}</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data).map(([url, summary]) => {
              if (url === 'timestamp') return null;

              let sourceName = "SOURCE";
              try {
                 const hostname = new URL(url).hostname;
                 sourceName = hostname.replace("www.", "").split('.').slice(0, -1).join('.').toUpperCase();
              } catch(e) {}

              return (
                <Card key={url} className="overflow-hidden border-l-4 border-l-blue-500">
                  <CardContent className="pt-6">
                    <div className="mb-2 flex items-center gap-2 text-sm text-blue-600 font-semibold">
                      <ExternalLink className="h-3 w-3" />
                      <a href={url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                        {sourceName}
                      </a>
                    </div>
                    <div className="prose prose-sm dark:prose-invert">
                        <div dangerouslySetInnerHTML={{ __html: summary.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br/>') }} />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
