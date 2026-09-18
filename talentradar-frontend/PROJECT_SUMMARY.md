# TalentRadar AI - Premium Recruiter Platform

A next-generation AI-powered talent discovery platform built with modern web technologies. This is a full-stack recruitment intelligence system designed for enterprise recruiters to discover, rank, and analyze talent with unprecedented precision.

## Architecture Overview

**Framework:** Next.js 16 (App Router)
**Styling:** Tailwind CSS v4 with custom animations
**Charts:** Recharts for data visualization
**UI Components:** shadcn/ui with customizations

## Design System

### Color Palette
- **Primary:** #6C63FF (Vibrant Purple)
- **Secondary:** #8B5CF6 (Deep Purple)
- **Accent:** #06B6D4 (Cyan)
- **Success:** #10B981 (Emerald)
- **Warning:** #F59E0B (Amber)
- **Danger:** #EF4444 (Red)
- **Background Dark:** #0F172A (Deep Navy)
- **Card Dark:** #1E293B (Slate)
- **Border:** #334155 (Medium Slate)
- **Muted Text:** #94A3B8 (Light Slate)

### Custom Effects
- **Glow Animation:** Pulsing container glow effect for AI elements
- **Pulse Glow:** Drop shadow animation for highlighted elements
- **Shimmer:** Gradient shimmer effect across elements
- **Float:** Smooth floating animation for visual hierarchy
- **Glass Morphism:** Frosted glass effect for premium UI

## Pages

### 1. Landing Page (`/`)
The public-facing homepage showcasing TalentRadar's capabilities.

**Key Sections:**
- Navigation with sign-in and CTA buttons
- Hero section with "Discover Talent Beyond Keywords" headline
- Feature grid (6 capabilities highlighted)
- Demo CTA section
- Call-to-action section
- Footer with company links

**Visual Elements:**
- Dark mode gradient hero with animated blob effects
- Glassmorphic cards with hover effects
- Gradient text for key messaging
- Interactive CTAs to dashboard and hidden talent page

### 2. Recruiter Dashboard (`/dashboard`)
Main candidate discovery and ranking interface.

**Features:**
- **Navigation Tabs:** Quick access to Candidates, Hidden Talent, and Analytics
- **Search & Filter:** Real-time filtering by name, title, skills with advanced filter panel
- **Candidate List:** Scrollable list with AI score badges and quick preview
- **Candidate Detail Panel:** Expanded view with:
  - Profile header with glowing avatar
  - AI Match Score and Role Match scores
  - Years of experience
  - Contact information
  - AI-generated summary
  - Skills & expertise badges
  - Match breakdown with progress bars (Technical Skills, Experience, Cultural Fit, Growth Potential)
  - Action buttons (Send Message, View Full Profile)

**Styling:**
- Dark theme with glassmorphic cards
- Gradient profiles and glowing effects
- Smooth animations on selection
- Responsive grid layout

### 3. Hidden Talent Discovery (`/hidden-talent`)
The unique USP - discovering candidates with transferable skills.

**Hero Section:**
- Prominent "Hidden Talent Detected" AI badge with glowing effect
- Statistics showing average match confidence, candidates analyzed, skill transfer potential

**Candidate Cards:**
- Name and current role
- Match confidence percentage with badge
- Hidden match reason preview
- Interactive card selection with glow effect

**Candidate Detail View (When Selected):**
- **AI Badge:** Prominent "Hidden Talent Detected" indicator with confidence score
- **Match Confidence Meter:** Animated progress bar showing AI confidence (0-100%)
- **Candidate Information:**
  - Name, years of experience, current role, target role
- **Hidden Match Reason:** Explanation of why this candidate is a fit
- **Why Candidate Was Discovered:** AI reasoning and discovery logic
- **Transferable Skills:** Grid of skill badges showing cross-functional capabilities
- **Action Buttons:** View Full Profile, Send Message

**Visual Features:**
- Glassmorphic cards with gradient backgrounds
- Glowing elements for AI-detected sections
- Smooth hover and selection animations
- Gradient skill badges

### 4. Analytics Dashboard (`/analytics`)
Comprehensive talent pool and hiring metrics.

**KPI Cards (Top Row):**
- Average Match Score (76.2%)
- Hiring Success Rate (68%)
- High Risk Candidates (13)
- Hidden Talent Found (24)
- Each with trend indicators

**Charts (6 Total):**

1. **Candidate Score Distribution** (Bar Chart)
   - Shows distribution across score ranges (80-100, 60-79, 40-59, 20-39)
   - Color-coded by performance tier

2. **Risk Level Distribution** (Donut Chart)
   - Low Risk (52 candidates) - Green
   - Medium Risk (35 candidates) - Amber
   - High Risk (13 candidates) - Red

3. **Skill Demand Analysis** (Horizontal Bar Chart)
   - Demand vs Supply for 6 key skills (React, TypeScript, Node.js, Python, AWS, Docker)
   - Dual bars showing market gap

4. **Hiring Funnel** (Vertical Funnel)
   - Applications → Screening → Interview → Offer → Hired
   - Shows candidate dropout at each stage

5. **Candidate Experience Breakdown** (Stacked Area Chart)
   - Junior, Mid, Senior levels tracked over 6 months
   - Smooth trend visualization

6. **Future Potential Distribution** (Donut Chart)
   - High (34%), Medium (45%), Developing (21%)
   - Growth potential segmentation

**Design:**
- Stripe-inspired dark analytics aesthetic
- Recharts with custom dark theme tooltips
- Responsive grid layout (2 columns on larger screens)
- Consistent color scheme matching brand palette

## Components

### Dashboard Components
- **CandidateCard:** Mini profile card with quick stats
- **CandidateDetail:** Expanded detail panel with full analysis
- **FilterPanel:** Advanced filtering controls

### UI Components
- **Button:** Primary, outline, and ghost variants
- **Input:** Search and form inputs with styling

## Key Features

### AI-Powered Intelligence
- Match confidence scoring system
- Hidden talent discovery algorithm
- Risk level assessment
- Future potential predictions
- Explainable AI reasoning

### Modern UI/UX
- Dark mode enterprise aesthetic
- Glassmorphic design patterns
- Smooth animations and transitions
- Responsive layouts
- Accessibility considerations (WCAG)

### Data Visualization
- 6+ chart types using Recharts
- Real-time filtering
- Performance metrics dashboard
- Hiring funnel analysis

## Interactivity

### Navigation
- Sticky header with navigation tabs
- Smooth page transitions
- Back buttons on sub-pages
- Quick access to all major features

### User Actions
- Candidate selection with visual feedback
- Search filtering with real-time results
- Advanced filter toggle
- Candidate profile interactions
- Message and profile view CTAs

## Performance Optimizations

- Static prerendering for all routes
- Optimized images and assets
- CSS-in-JS for styling
- Recharts with responsive containers
- Lazy loading where applicable

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile-responsive design
- Touch-friendly interface elements

## Deployment

The project is built as a static site using Next.js, allowing for:
- Vercel deployment with automatic optimizations
- Edge functions support
- Fast global CDN distribution
- Zero cold starts

## Getting Started

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Run production server
pnpm start
```

## File Structure

```
/app
  /dashboard         - Recruiter dashboard
  /hidden-talent     - Hidden talent discovery
  /analytics         - Analytics dashboard
  /page.tsx          - Landing page
  /layout.tsx        - Root layout
  /globals.css       - Global styles & theme

/components
  /dashboard         - Dashboard components
  /ui                - Reusable UI components
```

## Development Notes

### Design Decisions
- Dark theme chosen for modern enterprise feel and reduced eye strain
- Enterprise color palette for professionalism
- Glassmorphic effects for premium perception
- Recharts for complex data visualization
- Mock data for demo purposes (easily replaceable with API)

### Future Enhancements
- Authentication system (Better Auth + Neon recommended)
- Real-time data updates with WebSockets
- User preferences and saved searches
- Integration with ATS systems
- Email notifications
- Candidate messaging system
- Video interview playback
- Export and reporting features

## Project Size

- **Pages:** 4 main pages
- **Components:** 8+ custom components
- **Charts:** 6 different chart types
- **Color Palette:** 8+ semantic colors
- **Animations:** 5+ custom animations
- **Mock Data:** 6+ candidate profiles with detailed metrics

---

Built with Next.js 16, Tailwind CSS v4, Recharts, and shadcn/ui.
Ready for enterprise deployment and investor pitch.
