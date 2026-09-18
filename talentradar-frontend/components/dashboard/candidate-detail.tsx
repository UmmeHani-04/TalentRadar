'use client'

import { useState } from 'react'
import { Star, MapPin, Briefcase, Mail, ExternalLink, MessageSquare, Heart } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Candidate {
  id: string
  name: string
  title: string
  location: string
  experience: number
  skills: string[]
  aiScore: number
  matchScore: number
  summary: string
  image: string
  risk?: string
  semantic_score?: number
  experience_score?: number
  domain_score?: number
  momentum_score?: number
  hidden_talent_score?: number
  behavior_score?: number
  potential_score?: number
  authenticity_score?: number
}

interface CandidateDetailProps {
  candidate: Candidate
}

export default function CandidateDetail({ candidate }: CandidateDetailProps) {
  const [isSaved, setIsSaved] = useState(false)

  return (
    <div className="glass rounded-2xl border-border/40 overflow-hidden h-full flex flex-col">
      {/* Header with Background */}
      <div className="relative bg-gradient-to-r from-primary/10 to-accent/10 p-6 border-b border-border/40 overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 right-0 w-40 h-40 bg-primary/20 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-accent/20 rounded-full blur-3xl" />
        </div>
        <div className="relative">
            <div className="flex items-start justify-between mb-4">
            <div className="flex items-end gap-4">
              <div className="w-24 h-24 rounded-lg bg-gradient-to-br from-primary to-accent p-0.5 flex-shrink-0 glow">
                <div className="w-full h-full rounded-lg bg-card flex items-center justify-center text-2xl font-bold text-primary">
                  {candidate.name.split(' ').map(n => n[0]).join('')}
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold">{candidate.name}</h1>
                <p className="text-lg text-muted-foreground">{candidate.title}</p>
                {candidate.risk && candidate.risk !== 'LOW' && (
                  <span className={`inline-block mt-2 px-2 py-1 text-xs font-semibold rounded-md ${
                    candidate.risk === 'HIGH' ? 'bg-red-500/20 text-red-500 border border-red-500/30' : 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30'
                  }`}>
                    Risk: {candidate.risk}
                  </span>
                )}
              </div>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setIsSaved(!isSaved)}
              className={isSaved ? 'border-primary/40 bg-primary/5' : ''}
            >
              <Heart className={`w-4 h-4 ${isSaved ? 'fill-current text-primary' : ''}`} />
            </Button>
          </div>

          {/* AI Scores */}
          <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg bg-background/50 p-3 border border-border/40">
            <p className="text-xs text-muted-foreground mb-1">AI Match Score</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-primary">{candidate.aiScore}%</span>
            </div>
          </div>
          <div className="rounded-lg bg-background/50 p-3 border border-border/40">
            <p className="text-xs text-muted-foreground mb-1">Role Match</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-accent">{candidate.matchScore}%</span>
            </div>
          </div>
          <div className="rounded-lg bg-background/50 p-3 border border-border/40">
            <p className="text-xs text-muted-foreground mb-1">Experience</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{candidate.experience}</span>
              <span className="text-xs text-muted-foreground">years</span>
            </div>
          </div>
        </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Location & Contact */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Contact Info</h2>
          <div className="flex items-center gap-3 text-sm">
            <MapPin className="w-4 h-4 text-primary flex-shrink-0" />
            <span>{candidate.location}</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <Mail className="w-4 h-4 text-primary flex-shrink-0" />
            <span className="text-muted-foreground">{candidate.name.toLowerCase().replace(' ', '.')}@email.com</span>
          </div>
        </div>

        {/* Summary */}
        <div>
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">Explainable AI Summary</h2>
          <div className="rounded-lg bg-primary/5 border border-primary/20 p-4 whitespace-pre-wrap font-mono text-sm">
            {candidate.summary.replace(/\\n/g, '\n')}
          </div>
        </div>

        {/* Skills */}
        <div>
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">Skills & Expertise</h2>
          <div className="flex flex-wrap gap-2">
            {candidate.skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-medium border border-primary/20"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Compatibility Breakdown */}
        <div>
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">Match Breakdown (8 Dimensions)</h2>
          <div className="space-y-3">
            {[
              { label: 'Semantic Match', score: candidate.semantic_score ?? Math.round(candidate.aiScore) },
              { label: 'Experience Level', score: candidate.experience_score ?? Math.round(candidate.aiScore) },
              { label: 'Domain Expertise', score: candidate.domain_score ?? Math.round(candidate.aiScore) },
              { label: 'Career Momentum', score: candidate.momentum_score ?? Math.round(candidate.aiScore) },
              { label: 'Hidden Talent', score: candidate.hidden_talent_score ?? Math.round(candidate.aiScore) },
              { label: 'Future Potential', score: candidate.potential_score ?? Math.round(candidate.aiScore) },
              { label: 'Skill Authenticity', score: candidate.authenticity_score ?? Math.round(candidate.aiScore) },
              { label: 'Behavioral Signals', score: candidate.behavior_score ?? Math.round(candidate.aiScore) },
            ].map((item, idx) => (
              <div key={idx}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-foreground">{item.label}</span>
                  <span className="text-xs font-semibold text-primary">{Math.round(item.score)}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-500"
                    style={{ width: `${Math.round(item.score)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="border-t border-border/40 p-6 bg-card/50 space-y-3">
        <Button className="w-full bg-primary hover:bg-primary/90 gap-2" onClick={() => window.location.href = `mailto:${candidate.name.toLowerCase().replaceAll(' ', '.')}@example.com`}>
          <Mail className="w-4 h-4" />
          Send Message
        </Button>
        <Button variant="outline" className="w-full border-border/40 gap-2" onClick={() => window.open(`https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(candidate.name)}`, '_blank')}>
          <ExternalLink className="w-4 h-4" />
          View Full Profile
        </Button>
      </div>
    </div>
  )
}
