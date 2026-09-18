'use client'

import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Users, TrendingUp, Sparkles, Brain, Briefcase, BarChart3, Eye, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { getCandidates, getAnalytics } from '@/app/lib/api'
import type { CandidateSummary, AnalyticsResponse } from '@/app/lib/types'

function KPICard({ label, value, icon: Icon }: any) {
  return (
    <div className="card-modern p-6 border-l-4 border-l-primary flex items-start justify-between">
      <div>
        <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">{label}</p>
        <p className="text-3xl font-bold text-foreground">{value}</p>
      </div>
      {Icon && (
        <div className="p-3 rounded-xl bg-primary/10 text-primary">
          <Icon className="w-6 h-6" />
        </div>
      )}
    </div>
  )
}

function buildScoreDistribution(candidates: CandidateSummary[]) {
  const buckets = [
    { range: '90-100', count: 0, fill: '#10B981' },
    { range: '80-89', count: 0, fill: '#06B6D4' },
    { range: '70-79', count: 0, fill: '#6C63FF' },
    { range: '60-69', count: 0, fill: '#F59E0B' },
    { range: '<60', count: 0, fill: '#EF4444' }
  ]
  for (const c of candidates) {
    const s = c.score > 1 ? c.score : c.score * 100
    if (s >= 90) buckets[0].count++
    else if (s >= 80) buckets[1].count++
    else if (s >= 70) buckets[2].count++
    else if (s >= 60) buckets[3].count++
    else buckets[4].count++
  }
  return buckets
}

function buildRiskDistribution(riskMap: Record<string, number>) {
  const total = Object.values(riskMap).reduce((a, b) => a + b, 0)
  return [
    { name: 'Low Risk', value: riskMap['LOW'] || 0, fill: '#10B981' },
    { name: 'Medium Risk', value: riskMap['MEDIUM'] || 0, fill: '#F59E0B' },
    { name: 'High Risk', value: riskMap['HIGH'] || 0, fill: '#EF4444' }
  ].filter(b => b.value > 0).map(b => ({
    ...b,
    percentage: total > 0 ? Math.round((b.value / total) * 100) : 0
  }))
}

export default function DashboardPage() {
  const router = useRouter()
  
  const [candidates, setCandidates] = useState<CandidateSummary[]>([])
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [candRes, analyticsRes] = await Promise.all([getCandidates(), getAnalytics()])
        setCandidates(candRes.results)
        setAnalytics(analyticsRes)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const scoreDistribution = useMemo(() => buildScoreDistribution(candidates), [candidates])
  const riskDistribution = useMemo(() => analytics?.risk_distribution ? buildRiskDistribution(analytics.risk_distribution) : [], [analytics])

  const totalCandidates = analytics?.total_candidates || candidates.length
  const topMatches = candidates.filter(c => (c.score > 1 ? c.score : c.score * 100) >= 80).length
  const hiddenTalents = analytics?.hidden_talent_count || 0
  const avgScore = analytics?.average_score ? `${(analytics.average_score > 1 ? analytics.average_score : analytics.average_score * 100).toFixed(1)}%` : '0%'

  // Top 5 candidates for Recent Rankings
  const topCandidates = [...candidates].sort((a, b) => b.score - a.score).slice(0, 5)

  return (
    <div className="min-h-screen bg-background text-foreground pb-20">
      <header className="border-b border-border bg-background sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 hover:opacity-70 transition">
              <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-bold text-foreground">TalentRadar</span>
            </Link>
          </div>
          {/* Navigation Tabs */}
          <div className="flex items-center gap-8 border-t border-border pt-4 -mx-4 px-4">
            <button className="text-sm font-medium text-foreground border-b-2 border-foreground pb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Dashboard
            </button>
            <Link href="/candidates" className="text-sm font-medium text-muted-foreground hover:text-foreground pb-4 flex items-center gap-2 transition">
              <Briefcase className="w-4 h-4" />
              Ranking
            </Link>
            <Link href="/hidden-talent" className="text-sm font-medium text-muted-foreground hover:text-foreground pb-4 flex items-center gap-2 transition">
              <TrendingUp className="w-4 h-4" />
              Hidden Talent
            </Link>
            <Link href="/analytics" className="text-sm font-medium text-muted-foreground hover:text-foreground pb-4 flex items-center gap-2 transition">
              <BarChart3 className="w-4 h-4" />
              Analytics
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
            <p className="text-muted-foreground">Loading Dashboard Data...</p>
          </div>
        ) : (
          <>
            {/* Top KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <KPICard label="Total Candidates" value={`${totalCandidates} Analyzed`} icon={Users} />
              <KPICard label="Top Matches" value={`${topMatches} Strong Matches`} icon={TrendingUp} />
              <KPICard label="Hidden Talent" value={`${hiddenTalents} Discovered`} icon={Sparkles} />
              <KPICard label="Average Match Score" value={avgScore} icon={BarChart3} />
            </div>

            <div className="grid lg:grid-cols-2 gap-8 mb-8">
              {/* Score Distribution Chart */}
              <div className="card-modern rounded-2xl p-6 border-border/50">
                <h3 className="text-lg font-bold mb-6">Score Distribution</h3>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={scoreDistribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="range" stroke="#888" tick={{ fill: '#888' }} axisLine={false} tickLine={false} />
                      <YAxis stroke="#888" tick={{ fill: '#888' }} axisLine={false} tickLine={false} />
                      <Tooltip
                        cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                        contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                      />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={40}>
                        {scoreDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Risk Distribution Chart */}
              <div className="card-modern rounded-2xl p-6 border-border/50">
                <h3 className="text-lg font-bold mb-6">Risk Distribution</h3>
                <div className="flex items-center">
                  <div className="h-[250px] w-1/2">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={riskDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={2} dataKey="value" stroke="none">
                          {riskDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="w-1/2 flex flex-col gap-4 pl-4">
                    {riskDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-sm">
                          <div className="w-3 h-3 rounded-full shadow-inner" style={{ backgroundColor: item.fill }} />
                          <span className="text-muted-foreground">{item.name}</span>
                        </div>
                        <span className="font-bold">{item.percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Rankings Table */}
            <div className="card-modern rounded-2xl overflow-hidden border-border/50">
              <div className="p-6 border-b border-border/20 flex justify-between items-center">
                <h3 className="text-lg font-bold">Recent Top Candidates</h3>
                <Button variant="ghost" size="sm" onClick={() => router.push('/candidates')}>View All</Button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-card/50 border-b border-border/20 text-xs text-muted-foreground">
                      <th className="p-4 font-semibold uppercase tracking-wider">Candidate</th>
                      <th className="p-4 font-semibold uppercase tracking-wider">Score</th>
                      <th className="p-4 font-semibold uppercase tracking-wider">Risk</th>
                      <th className="p-4 font-semibold uppercase tracking-wider text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topCandidates.map((c) => {
                      const name = c.profile.anonymized_name || c.candidate_id
                      const score = Math.round(c.score > 1 ? c.score : c.score * 100)
                      let riskColor = 'bg-gray-500/20 text-gray-400'
                      if (c.risk === 'LOW') riskColor = 'bg-green-500/20 text-green-400'
                      if (c.risk === 'MEDIUM') riskColor = 'bg-yellow-500/20 text-yellow-400'
                      if (c.risk === 'HIGH') riskColor = 'bg-red-500/20 text-red-400'

                      return (
                        <tr key={c.candidate_id} className="border-b border-border/10 hover:bg-card/50 transition-colors">
                          <td className="p-4">
                            <div className="flex items-center gap-3">
                              <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${c.candidate_id}`} alt={name} className="w-8 h-8 rounded-full bg-card" />
                              <span className="font-semibold text-sm">{name}</span>
                            </div>
                          </td>
                          <td className="p-4">
                            <span className="font-bold text-sm text-primary">{score}%</span>
                          </td>
                          <td className="p-4">
                            <span className={`px-2 py-1 rounded-full text-[10px] font-bold tracking-wide ${riskColor}`}>
                              {c.risk || 'UNKNOWN'}
                            </span>
                          </td>
                          <td className="p-4 text-right">
                            <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => router.push(`/candidates/${c.candidate_id}`)}>
                              <Eye className="w-3 h-3 mr-1" /> View Details
                            </Button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
