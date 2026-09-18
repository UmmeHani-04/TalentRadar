'use client'

import { useState } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface FilterPanelProps {
  filters: {
    experience: [number, number]
    aiScore: [number, number]
    skills: string[]
  }
  setFilters: (filters: any) => void
}

const COMMON_SKILLS = [
  'React', 'Node.js', 'Python', 'TypeScript', 'AWS', 'Docker',
  'PostgreSQL', 'Product Strategy', 'User Research', 'Analytics',
  'Leadership', 'Sales', 'Figma', 'Machine Learning'
]

export default function FilterPanel({ filters, setFilters }: FilterPanelProps) {
  return (
    <div className="rounded-lg border border-border/40 bg-card p-6 space-y-6">
      {/* Experience Filter */}
      <div>
        <label className="text-sm font-semibold mb-3 block">Years of Experience</label>
        <div className="space-y-4">
          <input
            type="range"
            min="0"
            max="20"
            value={filters.experience[1]}
            onChange={(e) => setFilters({
              ...filters,
              experience: [filters.experience[0], parseInt(e.target.value)]
            })}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{filters.experience[0]} years</span>
            <span>{filters.experience[1]} years</span>
          </div>
        </div>
      </div>

      {/* AI Score Filter */}
      <div>
        <label className="text-sm font-semibold mb-3 block">Minimum AI Score</label>
        <div className="space-y-4">
          <input
            type="range"
            min="0"
            max="100"
            value={filters.aiScore[0]}
            onChange={(e) => setFilters({
              ...filters,
              aiScore: [parseInt(e.target.value), filters.aiScore[1]]
            })}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{filters.aiScore[0]}%</span>
            <span>{filters.aiScore[1]}%</span>
          </div>
        </div>
      </div>

      {/* Skills Filter */}
      <div>
        <label className="text-sm font-semibold mb-3 block">Skills</label>
        <div className="grid grid-cols-2 gap-2">
          {COMMON_SKILLS.map((skill) => (
            <button
              key={skill}
              onClick={() => setFilters({
                ...filters,
                skills: filters.skills.includes(skill)
                  ? filters.skills.filter(s => s !== skill)
                  : [...filters.skills, skill]
              })}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                filters.skills.includes(skill)
                  ? 'bg-primary/20 border border-primary/40 text-primary'
                  : 'bg-muted/30 border border-border/40 text-foreground hover:border-primary/40'
              }`}
            >
              {skill}
            </button>
          ))}
        </div>
      </div>

      {/* Reset Button */}
      <Button
        variant="outline"
        size="sm"
        className="w-full border-border/40"
        onClick={() => setFilters({
          experience: [0, 15],
          aiScore: [70, 100],
          skills: []
        })}
      >
        Reset Filters
      </Button>
    </div>
  )
}
