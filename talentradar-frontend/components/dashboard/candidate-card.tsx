import { Star, MapPin, Briefcase } from 'lucide-react'
import Image from 'next/image'

interface Candidate {
  id: number
  name: string
  title: string
  location: string
  experience: number
  skills: string[]
  aiScore: number
  matchScore: number
  image: string
}

interface CandidateCardProps {
  candidate: Candidate
  isSelected: boolean
}

export default function CandidateCard({ candidate, isSelected }: CandidateCardProps) {
  return (
    <div className={`rounded-lg border transition-all duration-200 p-4 ${
      isSelected
        ? 'border-primary bg-primary/5'
        : 'border-border/40 bg-card hover:border-primary/40 hover:bg-card/80'
    }`}>
      <div className="flex gap-3 mb-3">
        <div className="w-12 h-12 rounded-full flex-shrink-0 bg-gradient-to-br from-primary to-accent p-0.5">
          <div className="w-full h-full rounded-full bg-card flex items-center justify-center text-xs font-bold text-primary">
            {candidate.name.split(' ').map(n => n[0]).join('')}
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm truncate">{candidate.name}</h3>
          <p className="text-xs text-muted-foreground truncate">{candidate.title}</p>
        </div>
      </div>
      
      <div className="flex items-center justify-between mb-3">
        <div className="flex gap-2">
          <div className="px-2 py-1 rounded bg-primary/10 text-primary text-xs font-semibold">
            AI: {candidate.aiScore}%
          </div>
          <div className="px-2 py-1 rounded bg-accent/10 text-accent text-xs font-semibold">
            Match: {candidate.matchScore}%
          </div>
        </div>
      </div>

      <div className="space-y-2 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          <span>{candidate.location}</span>
        </div>
        <div className="flex items-center gap-1">
          <Briefcase className="w-3 h-3" />
          <span>{candidate.experience} years experience</span>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {candidate.skills.slice(0, 2).map((skill, idx) => (
          <span key={idx} className="px-2 py-1 rounded-full bg-muted/50 text-foreground text-xs">
            {skill}
          </span>
        ))}
        {candidate.skills.length > 2 && (
          <span className="px-2 py-1 rounded-full bg-muted/50 text-foreground text-xs">
            +{candidate.skills.length - 2}
          </span>
        )}
      </div>
    </div>
  )
}
