'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Search, Filter, SortDesc, Download, Eye, Brain, Briefcase, TrendingUp, BarChart3, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { getCandidates, rankCandidates } from '@/app/lib/api'
import type { CandidateSummary } from '@/app/lib/types'

export default function CandidatesRankingPage() {
  const router = useRouter()
  
  const [toastMsg, setToastMsg] = useState<{title: string, description: string} | null>(null)
  const toast = ({title, description}: {title: string, description: string, variant?: string}) => {
    setToastMsg({title, description})
    setTimeout(() => setToastMsg(null), 3000)
  }
  
  // Ranking State
  const [jd, setJd] = useState('Need Senior AI Engineer with Python, LLM, FAISS.')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  
  // Candidates State
  const [candidates, setCandidates] = useState<CandidateSummary[]>([])
  const [loading, setLoading] = useState(true)
  
  // Filter/Sort/Search State
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'score' | 'risk' | 'experience'>('score')
  const [filterRisk, setFilterRisk] = useState<string>('ALL')
  const [filterExperience, setFilterExperience] = useState<string>('ALL')
  const [filterScore, setFilterScore] = useState<string>('ALL')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    loadCandidates()
  }, [])

  const loadCandidates = async () => {
    setLoading(true)
    try {
      const response = await getCandidates()
      setCandidates(response.results)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!jd.trim()) return
    setIsAnalyzing(true)
    setAnalysisProgress(0)

    // Simulate progress steps for the demo
    const interval = setInterval(() => {
      setAnalysisProgress(p => (p < 90 ? p + 15 : p))
    }, 1000)

    try {
      await rankCandidates(jd)
      clearInterval(interval)
      setAnalysisProgress(100)
      
      // Reload candidates
      await loadCandidates()
      
      setTimeout(() => {
        setIsAnalyzing(false)
        setAnalysisProgress(0)
      }, 500)
    } catch (err) {
      clearInterval(interval)
      setIsAnalyzing(false)
      console.error('Ranking failed:', err)
      toast({
        title: "Analysis Failed",
        description: "Failed to run AI pipeline.",
        variant: "destructive",
      })
    }
  }

  const handleDownloadReport = (candidateName: string) => {
    const reportContent = `TALENTRADAR AI - CANDIDATE ANALYSIS REPORT\n\nCandidate: ${candidateName}\nAnalysis Date: ${new Date().toLocaleDateString()}\nStatus: CONFIDENTIAL\n\nAI Match Evaluation:\n- Strong semantic match detected\n- Low risk indicators\n- High career momentum trajectory\n\n(Detailed skill matrices and full AI explanations are available in the web dashboard.)`
    const blob = new Blob([reportContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${candidateName.replaceAll(' ', '_')}_Analysis.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast({
      title: "Download Complete",
      description: `Report for ${candidateName} has been saved.`,
    })
  }

  // Derived filtered & sorted candidates
  const processedCandidates = candidates
    .filter(c => {
      const name = c.profile.anonymized_name || c.candidate_id
      const title = c.profile.current_title || ''
      const exp = c.profile.years_of_experience || 0
      
      // Search
      const searchMatch = !searchQuery || 
        name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.skills.some(s => {
          const sName = typeof s === 'string' ? s : s.name
          return sName && sName.toLowerCase().includes(searchQuery.toLowerCase())
        })
        
      // Risk Filter
      const riskMatch = filterRisk === 'ALL' || c.risk === filterRisk
      
      // Experience Filter
      let expMatch = true
      if (filterExperience === '0-2') expMatch = exp <= 2
      else if (filterExperience === '3-5') expMatch = exp >= 3 && exp <= 5
      else if (filterExperience === '5+') expMatch = exp > 5
      
      // Score Filter
      let scoreMatch = true
      const s = c.score > 1 ? c.score : c.score * 100
      if (filterScore === '>80') scoreMatch = s > 80
      else if (filterScore === '>90') scoreMatch = s > 90

      return searchMatch && riskMatch && expMatch && scoreMatch
    })
    .sort((a, b) => {
      if (sortBy === 'score') return b.score - a.score
      if (sortBy === 'experience') return (b.profile.years_of_experience || 0) - (a.profile.years_of_experience || 0)
      if (sortBy === 'risk') {
        const riskOrder = { 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'UNKNOWN': 4 }
        return (riskOrder[a.risk as keyof typeof riskOrder] || 4) - (riskOrder[b.risk as keyof typeof riskOrder] || 4)
      }
      return 0
    })

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
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
            <Link href="/dashboard" className="text-sm font-medium text-muted-foreground hover:text-foreground pb-4 flex items-center gap-2 transition">
              <BarChart3 className="w-4 h-4" />
              Dashboard
            </Link>
            <button className="text-sm font-medium text-foreground border-b-2 border-foreground pb-4 flex items-center gap-2">
              <Briefcase className="w-4 h-4" />
              Ranking
            </button>
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
        
        {/* Job Description Input Section */}
        <div className="card-modern p-6 rounded-2xl mb-8 relative overflow-hidden">
          {isAnalyzing && (
            <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-10 flex flex-col items-center justify-center">
              <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
              <h3 className="text-xl font-bold mb-2">Analyzing Candidates</h3>
              <p className="text-muted-foreground mb-4">Running Semantic Matcher & AI Engines...</p>
              <div className="w-64 h-2 bg-card rounded-full overflow-hidden">
                <div className="h-full bg-primary transition-all duration-500" style={{ width: `${analysisProgress}%` }} />
              </div>
            </div>
          )}
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Search className="w-5 h-5 text-primary" />
            Job Description Analysis
          </h2>
          <div className="flex flex-col gap-4">
            <Textarea 
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste Job Description here..."
              className="min-h-[120px] bg-card border-border/50 text-base"
            />
            <div className="flex justify-end">
              <Button onClick={handleAnalyze} size="lg" className="gap-2 px-8 font-semibold">
                <Brain className="w-4 h-4" />
                Analyze Candidates
              </Button>
            </div>
          </div>
        </div>

        {/* Candidate Ranking Tools */}
        <div className="flex flex-col gap-4 mb-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search by Name, Skills, or Role..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-card border-border/40"
              />
            </div>
            <Button variant="outline" onClick={() => setShowFilters(!showFilters)} className="gap-2">
              <Filter className="w-4 h-4" />
              Filters
            </Button>
            <div className="flex items-center gap-2 border border-border/40 rounded-md p-1 bg-card">
              <span className="text-sm text-muted-foreground pl-3 pr-2 border-r border-border/40">Sort By</span>
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value as any)}
                className="bg-transparent border-none text-sm outline-none pr-4 cursor-pointer"
              >
                <option value="score">Highest Score</option>
                <option value="risk">Lowest Risk</option>
                <option value="experience">Most Experience</option>
              </select>
            </div>
          </div>

          {/* Expanded Filters */}
          {showFilters && (
            <div className="grid grid-cols-3 gap-4 p-4 card-modern rounded-lg bg-card/50">
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase mb-2 block">Experience Filter</label>
                <select value={filterExperience} onChange={(e) => setFilterExperience(e.target.value)} className="w-full bg-background border border-border/40 rounded p-2 text-sm">
                  <option value="ALL">All Experience Levels</option>
                  <option value="0-2">0-2 Years</option>
                  <option value="3-5">3-5 Years</option>
                  <option value="5+">5+ Years</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase mb-2 block">Risk Filter</label>
                <select value={filterRisk} onChange={(e) => setFilterRisk(e.target.value)} className="w-full bg-background border border-border/40 rounded p-2 text-sm">
                  <option value="ALL">All Risk Levels</option>
                  <option value="LOW">Low Risk</option>
                  <option value="MEDIUM">Medium Risk</option>
                  <option value="HIGH">High Risk</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase mb-2 block">Score Filter</label>
                <select value={filterScore} onChange={(e) => setFilterScore(e.target.value)} className="w-full bg-background border border-border/40 rounded p-2 text-sm">
                  <option value="ALL">All Scores</option>
                  <option value=">80">Above 80%</option>
                  <option value=">90">Above 90%</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Candidate Table */}
        <div className="card-modern rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-card border-b border-border/50 text-sm text-muted-foreground">
                  <th className="p-4 font-semibold uppercase tracking-wider">Candidate</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Experience</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Match Score</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Risk</th>
                  <th className="p-4 font-semibold uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                      Loading candidates...
                    </td>
                  </tr>
                ) : processedCandidates.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      No candidates found matching criteria.
                    </td>
                  </tr>
                ) : (
                  processedCandidates.map((c) => {
                    const name = c.profile.anonymized_name || c.candidate_id
                    const title = c.profile.current_title || 'Software Engineer'
                    const exp = Math.round(c.profile.years_of_experience || 0)
                    const score = Math.round(c.score > 1 ? c.score : c.score * 100)
                    
                    let riskColor = 'bg-gray-500/20 text-gray-400'
                    if (c.risk === 'LOW') riskColor = 'bg-green-500/20 text-green-400'
                    if (c.risk === 'MEDIUM') riskColor = 'bg-yellow-500/20 text-yellow-400'
                    if (c.risk === 'HIGH') riskColor = 'bg-red-500/20 text-red-400'

                    return (
                      <tr key={c.candidate_id} className="border-b border-border/20 hover:bg-card/50 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${c.candidate_id}`} alt={name} className="w-10 h-10 rounded-full bg-card" />
                            <div>
                              <div className="font-semibold text-foreground">{name}</div>
                              <div className="text-xs text-muted-foreground">{title}</div>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 text-sm">{exp} Years</td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <span className="font-bold">{score}%</span>
                            <div className="w-24 h-2 bg-card rounded-full overflow-hidden">
                              <div className="h-full bg-primary" style={{ width: `${score}%` }} />
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold tracking-wide ${riskColor}`}>
                            {c.risk || 'UNKNOWN'}
                          </span>
                        </td>
                        <td className="p-4 text-right space-x-2">
                          <Button variant="outline" size="sm" onClick={() => router.push(`/candidates/${c.candidate_id}`)}>
                            <Eye className="w-4 h-4 mr-1" /> View Profile
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDownloadReport(name)}>
                            <Download className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {toastMsg && (
          <div className="fixed bottom-4 right-4 bg-card border border-border p-4 rounded-xl shadow-lg z-50 animate-in slide-in-from-bottom-5">
            <h4 className="font-bold">{toastMsg.title}</h4>
            <p className="text-sm text-muted-foreground">{toastMsg.description}</p>
          </div>
        )}
      </main>
    </div>
  )
}
