'use client'

import Link from 'next/link'
import { ArrowRight, TrendingUp, Users, Brain, BarChart3, Sparkles, CheckCircle2, FileText, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <header className="sticky top-0 z-50 border-b border-border bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
              <Brain className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">TalentRadar</span>
          </div>
          <nav className="hidden md:flex gap-8 text-sm text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition">Features</a>
            <a href="#demo" className="hover:text-foreground transition">Demo</a>
            <a href="/" className="hover:text-foreground transition">About</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/dashboard">
              <Button size="sm" className="bg-primary text-primary-foreground hover:bg-secondary">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 sm:py-32 border-b border-border">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6 text-balance text-foreground">
            Discover Talent Beyond Keywords
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-12 text-balance leading-relaxed">
            TalentRadar uses advanced AI to identify candidates with transferable skills and high potential, regardless of exact job title matches. Discover talent your competitors miss.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="bg-primary text-primary-foreground hover:bg-secondary">
                Get Started <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="outline" className="border-border hover:border-secondary hover:bg-card">
                Watch Demo <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
          
          {/* Demo Area */}
          <div className="mt-16 rounded border border-border bg-card overflow-hidden">
            <div className="aspect-video bg-muted flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground text-sm">Advanced analytics dashboard included</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 sm:py-32 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-foreground">
              Key Features
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Professional tools for modern talent acquisition teams
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: Brain,
                title: "Semantic Matching",
                description: "AI understands the meaning behind skills, not just keywords."
              },
              {
                icon: Sparkles,
                title: "Hidden Talent Discovery",
                description: "Find candidates with highly transferable skills that traditional ATS misses."
              },
              {
                icon: CheckCircle2,
                title: "Skill Authenticity",
                description: "Verify if claimed skills are backed by real project experience."
              },
              {
                icon: FileText,
                title: "Explainable AI",
                description: "Get detailed reasoning behind every candidate's match score."
              },
              {
                icon: AlertTriangle,
                title: "Risk Analysis",
                description: "Automatically detect red flags like inconsistent career paths."
              },
              {
                icon: TrendingUp,
                title: "Career Momentum",
                description: "Evaluate the trajectory and growth potential of every candidate."
              }
            ].map((feature, idx) => (
              <div key={idx} className="card-modern p-6">
                <feature.icon className="w-8 h-8 text-primary mb-4" />
                <h3 className="text-lg font-semibold mb-2 text-foreground">{feature.title}</h3>
                <p className="text-muted-foreground text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 sm:py-32 border-b border-border">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-6 text-foreground">
            Ready to get started?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl">
            Launch the interactive demo to see TalentRadar in action. Explore candidate profiles, analytics, and AI-powered insights.
          </p>
          <Link href="/dashboard">
            <Button size="lg" className="bg-primary text-primary-foreground hover:bg-secondary">
              Try Demo Now <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
                <Brain className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-semibold text-foreground">TalentRadar</span>
            </div>
            <div className="flex gap-6 text-sm text-muted-foreground">
              <a href="/" className="hover:text-foreground transition">Privacy</a>
              <a href="/" className="hover:text-foreground transition">Terms</a>
              <a href="/" className="hover:text-foreground transition">Contact</a>
            </div>
          </div>
          <div className="border-t border-border pt-8 mt-8 text-center text-sm text-muted-foreground">
            <p>© 2024 TalentRadar. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
