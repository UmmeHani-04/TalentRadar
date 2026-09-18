'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Brain, FileText, CheckCircle2, Loader2, Sparkles, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { rankCandidates } from '@/app/lib/api'

export default function NewJobPage() {
  const router = useRouter()
  const [jobDescription, setJobDescription] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    { text: 'Parsing Job Description...', icon: FileText },
    { text: 'Extracting Hidden Requirements...', icon: Sparkles },
    { text: 'Running Semantic Matcher...', icon: Brain },
    { text: 'Evaluating Risk & Authenticity...', icon: AlertTriangle },
    { text: 'Finalizing AI Rankings...', icon: CheckCircle2 }
  ]

  useEffect(() => {
    if (!isProcessing) return
    const interval = setInterval(() => {
      setCurrentStep(prev => (prev < steps.length - 1 ? prev + 1 : prev))
    }, 4000)
    return () => clearInterval(interval)
  }, [isProcessing, steps.length])

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) return
    setIsProcessing(true)
    setCurrentStep(0)
    try {
      await rankCandidates(jobDescription)
      router.push('/dashboard')
    } catch (err) {
      console.error(err)
      setIsProcessing(false)
      alert("An error occurred while ranking candidates.")
    }
  }

  if (isProcessing) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
        <div className="w-24 h-24 mb-12 relative">
          <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl animate-pulse" />
          <div className="relative w-full h-full rounded-full border-t-2 border-r-2 border-primary animate-spin" />
          <Brain className="absolute inset-0 m-auto w-10 h-10 text-primary animate-pulse" />
        </div>
        
        <div className="space-y-6 w-full max-w-md">
          {steps.map((step, idx) => {
            const Icon = step.icon
            const isCompleted = idx < currentStep
            const isActive = idx === currentStep
            
            return (
              <div 
                key={idx} 
                className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-500 ${
                  isActive ? 'bg-primary/10 border border-primary/20 scale-105' : 
                  isCompleted ? 'opacity-50' : 'opacity-20'
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0" />
                ) : isActive ? (
                  <Loader2 className="w-6 h-6 text-primary animate-spin flex-shrink-0" />
                ) : (
                  <Icon className="w-6 h-6 text-muted-foreground flex-shrink-0" />
                )}
                <span className={`font-medium ${isActive ? 'text-primary' : 'text-foreground'}`}>
                  {step.text}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6 md:p-12">
      <div className="max-w-3xl mx-auto space-y-8 mt-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 tracking-tight">AI Talent Discovery</h1>
          <p className="text-lg text-muted-foreground">Paste your job description below. TalentRadar AI will semantically match, evaluate hidden requirements, and intelligently rank your candidate pool.</p>
        </div>
        
        <div className="glass p-6 sm:p-8 rounded-3xl border border-border/40 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -z-10" />
          <textarea 
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            className="w-full h-72 bg-background/50 border border-border/50 rounded-xl p-6 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none font-mono text-sm leading-relaxed"
            placeholder="Need Senior AI Engineer with 5+ years experience in Python, LLM, FAISS, Docker..."
          />
          <div className="mt-8 flex justify-end">
            <Button 
              size="lg" 
              onClick={handleAnalyze} 
              disabled={!jobDescription.trim()}
              className="bg-primary text-primary-foreground hover:bg-primary/90 gap-2 h-12 px-8 text-lg font-medium"
            >
              <Brain className="w-5 h-5" />
              Analyze Candidates
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
