'use client'

import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowLeft, TrendingUp, Users, Flame, Zap, BarChart as BarChartIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { getAnalytics, getCandidates } from '@/app/lib/api'
import type { AnalyticsResponse, CandidateSummary } from '@/app/lib/types'

const EMPTY_SCORE_DISTRIBUTION = [
  { range: '90-100', count: 0, fill: '#10B981' },
  { range: '80-89', count: 0, fill: '#06B6D4' },
  { range: '70-79', count: 0, fill: '#6C63FF' },
  { range: '60-69', count: 0, fill: '#F59E0B' },
  { range: '<60', count: 0, fill: '#EF4444' }
]

const EMPTY_RISK = [
  { name: 'Low Risk', value: 0, percentage: 0, fill: '#10B981' },
  { name: 'Medium Risk', value: 0, percentage: 0, fill: '#F59E0B' },
  { name: 'High Risk', value: 0, percentage: 0, fill: '#EF4444' }
]

function KPICard({ label, value, subtext, icon: Icon, trend, trendValue }: any) {
  return (
    <div className="card-modern p-6 border-l-4 border-l-primary">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">{label}</p>
          <p className="text-4xl font-bold text-foreground">{value}</p>
          {subtext && <p className="text-sm text-muted-foreground mt-1">{subtext}</p>}
        </div>
        {Icon && (
          <div className="p-3 rounded-xl bg-primary/10 text-primary">
            <Icon className="w-8 h-8" />
          </div>
        )}
      </div>
      {trend && (
        <div className={`flex items-center gap-1 text-sm font-medium ${trend === 'up' ? 'text-success' : 'text-muted-foreground'}`}>
          <TrendingUp className={`w-4 h-4 ${trend === 'down' ? 'rotate-180' : ''}`} />
          {trendValue}
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
    const s = c.score * 100 // assuming score is 0.0 - 1.0, wait...
    // Let me check what c.score is. If it's already 80.5, it's 0-100.
    const finalScore = c.score > 1 ? c.score : c.score * 100
    
    if (finalScore >= 90) buckets[0].count++
    else if (finalScore >= 80) buckets[1].count++
    else if (finalScore >= 70) buckets[2].count++
    else if (finalScore >= 60) buckets[3].count++
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

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null)
  const [candidates, setCandidates] = useState<CandidateSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const loadData = async () => {
      try {
        const [analyticsRes, candidatesRes] = await Promise.all([
          getAnalytics(),
          getCandidates(),
        ])
        if (!active) return
        setAnalytics(analyticsRes)
        setCandidates(candidatesRes.results)
      } catch (err) {
        console.error(err)
        if (active) {
          setError('Unable to load analytics from backend.')
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    loadData()
    return () => {
      active = false
    }
  }, [])

  const scoreDistribution = useMemo(
    () => (candidates.length > 0 ? buildScoreDistribution(candidates) : EMPTY_SCORE_DISTRIBUTION),
    [candidates],
  )

  const riskDistribution = useMemo(
    () =>
      analytics?.risk_distribution
        ? buildRiskDistribution(analytics.risk_distribution)
        : EMPTY_RISK,
    [analytics],
  )

  const averageMatchScore = analytics?.average_score 
    ? `${(analytics.average_score > 1 ? analytics.average_score : analytics.average_score * 100).toFixed(1)}%` 
    : '0%'
    
  const totalCandidates = analytics?.total_candidates ?? 0
  const hiddenTalentCount = analytics?.hidden_talent_count ?? 0

  // Calculate top domains for hidden talent
  const topDomains = useMemo(() => {
    if (!analytics?.hidden_talent_ids || candidates.length === 0) {
      return ['Recommendation Systems', 'Search Systems', 'Data Engineering', 'NLP']
    }
    
    const hiddenSet = new Set(analytics.hidden_talent_ids)
    const hiddenCandidates = candidates.filter(c => hiddenSet.has(c.candidate_id))
    
    if (hiddenCandidates.length === 0) {
      return ['Recommendation Systems', 'Search Systems', 'Data Engineering', 'NLP']
    }

    const skillCounts: Record<string, number> = {}
    hiddenCandidates.forEach(c => {
      c.skills.forEach(s => {
        const skillName = typeof s === 'string' ? s : s.name
        if (skillName) {
          skillCounts[skillName] = (skillCounts[skillName] || 0) + 1
        }
      })
    })

    const sortedSkills = Object.entries(skillCounts)
      .sort((a, b) => b[1] - a[1])
      .map(entry => entry[0])

    if (sortedSkills.length === 0) {
      return ['Recommendation Systems', 'Search Systems', 'Data Engineering', 'NLP']
    }

    return sortedSkills.slice(0, 4)
  }, [analytics, candidates])

  return (
    <div className="min-h-screen bg-background text-foreground pb-20">
      {/* Header */}
      <header className="border-b border-border bg-background sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <div className="hidden sm:block">
              <h1 className="text-2xl font-bold flex items-center gap-2">
                Talent Pool Analytics
              </h1>
            </div>
          </div>
          <div className="text-xs text-muted-foreground">
            {loading ? 'Analyzing talent pool...' : error ? error : 'Live Insights'}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <div className="mb-8">
          <h2 className="text-3xl font-extrabold tracking-tight mb-2">What does the talent pool look like?</h2>
          <p className="text-muted-foreground text-lg">Overall insights across all analyzed candidates.</p>
        </div>

        {/* Top KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <KPICard
            label="Total Candidates Analyzed"
            value={String(totalCandidates)}
            icon={Users}
            trend="up"
            trendValue="Processed by AI pipeline"
          />
          <KPICard
            label="Average Match Score"
            value={averageMatchScore}
            icon={TrendingUp}
            trend="up"
            trendValue="Highly qualified pool"
          />
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Main Charts - Left Column */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Candidate Score Distribution */}
            <div className="card-modern rounded-2xl p-8 border-border/50 shadow-sm">
              <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                <BarChartIcon className="w-5 h-5 text-primary" /> 
                Candidate Score Distribution
              </h3>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={scoreDistribution} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="range" stroke="#888" tick={{ fill: '#888' }} axisLine={false} tickLine={false} />
                    <YAxis stroke="#888" tick={{ fill: '#888' }} axisLine={false} tickLine={false} />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                      contentStyle={{
                        backgroundColor: '#111',
                        border: '1px solid #333',
                        borderRadius: '12px',
                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
                      }}
                      itemStyle={{ color: '#fff', fontWeight: 'bold' }}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={60}>
                      {scoreDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Risk Distribution */}
            <div className="card-modern rounded-2xl p-8 border-border/50 shadow-sm">
              <h3 className="text-xl font-bold mb-6">Risk Distribution</h3>
              <div className="flex items-center">
                <div className="h-[300px] w-2/3">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={riskDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={80}
                        outerRadius={120}
                        paddingAngle={5}
                        dataKey="value"
                        stroke="none"
                      >
                        {riskDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#111',
                          border: '1px solid #333',
                          borderRadius: '12px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="w-1/3 flex flex-col gap-6">
                  {riskDistribution.map((item) => (
                    <div key={item.name} className="flex flex-col">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-4 h-4 rounded-full shadow-inner" style={{ backgroundColor: item.fill }} />
                        <span className="text-muted-foreground font-medium">{item.name}</span>
                      </div>
                      <span className="text-3xl font-bold">{item.percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
          </div>

          {/* USP Panel - Right Column */}
          <div className="lg:col-span-1 space-y-8">
            <div className="relative h-full">
              <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-accent/5 rounded-3xl blur-xl" />
              <div className="relative h-full bg-gradient-to-b from-card/80 to-background rounded-3xl border border-primary/20 p-8 shadow-2xl flex flex-col overflow-hidden">
                
                {/* Decorative background elements */}
                <div className="absolute -top-24 -right-24 w-48 h-48 bg-primary/20 rounded-full blur-3xl pulse-glow" />
                <div className="absolute top-4 right-4 text-4xl opacity-20">🔥</div>
                
                <h3 className="text-2xl font-black mb-8 text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent flex items-center gap-3">
                  <Flame className="w-8 h-8 text-primary" />
                  Hidden Talent Insights
                </h3>
                
                <div className="mb-10 p-6 bg-primary/5 rounded-2xl border border-primary/10 backdrop-blur-md">
                  <p className="text-6xl font-black text-foreground mb-2">{hiddenTalentCount}</p>
                  <p className="text-lg font-medium text-muted-foreground">candidates discovered through semantic matching.</p>
                </div>
                
                <div className="flex-1">
                  <h4 className="text-sm uppercase tracking-widest font-semibold text-primary mb-6 flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    Top Transferable Domains
                  </h4>
                  
                  <div className="space-y-4">
                    {topDomains.map((domain, idx) => (
                      <div 
                        key={idx} 
                        className="flex items-center p-4 bg-background/50 border border-border/50 rounded-xl hover:bg-primary/5 hover:border-primary/30 transition-colors"
                      >
                        <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold mr-4">
                          {idx + 1}
                        </div>
                        <span className="font-semibold text-lg">{domain}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            </div>
          </div>
          
        </div>
      </main>
    </div>
  )
}
