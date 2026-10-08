import { motion } from 'framer-motion'
import {
  ArrowRight, BookOpen, Brain, Check, ChevronRight, CirclePlay, FileSearch,
  FolderOpen, Gavel, LockKeyhole, Mail, Scale, ShieldCheck, Sparkles,
} from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { BrandMark } from '../components/layout'
import { Button, GlassCard, SectionLabel } from '../components/ui'
import { useAuth } from '../context/auth'

const helpCards = [
  { icon: Brain, title: 'Understand Your Case', text: 'Bring key facts, records, and questions into one clear workspace.' },
  { icon: ShieldCheck, title: 'Organize Evidence', text: 'Keep supporting material structured, traceable, and ready to review.' },
  { icon: FileSearch, title: 'Analyze Documents', text: 'Turn dense documents into reviewable information and next questions.' },
  { icon: BookOpen, title: 'Discover Legal References', text: 'Explore relevant material as references for further verification.' },
  { icon: Gavel, title: 'Find Similar Cases', text: 'Surface comparable patterns from available legal information.' },
  { icon: Sparkles, title: 'Build an Action Plan', text: 'Create a measured, structured view of possible next steps.' },
]

export function Home() {
  return (
    <div className="marketing-page">
      <header className="marketing-nav">
        <Link to="/" aria-label="DigiLaw home"><BrandMark /></Link>
        <nav aria-label="Marketing navigation"><a href="#how-it-works">How it works</a><a href="#responsible-ai">Responsible AI</a></nav>
        <div><Link className="marketing-login" to="/login">Sign in</Link><Link className="nav-cta" to="/register">Explore DigiLaw <ArrowRight size={15} /></Link></div>
      </header>

      <main>
        <section className="landing-hero">
          <motion.div className="hero-copy" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <SectionLabel icon={Sparkles}>AI-POWERED LEGAL INTELLIGENCE</SectionLabel>
            <h1>Understand your legal case.<br /><em>Know what comes next.</em></h1>
            <p>DigiLaw helps organize legal information, analyze evidence, understand documents, discover relevant legal references, and build structured next steps.</p>
            <div className="hero-actions"><Link className="button button-primary" to="/register">Explore DigiLaw <ArrowRight size={17} /></Link><a className="button button-quiet" href="#how-it-works"><CirclePlay size={17} /> See how it works</a></div>
            <p className="hero-trust"><ShieldCheck size={16} /> Built for informed review, not legal advice.</p>
          </motion.div>
          <motion.div className="hero-visual" initial={{ opacity: 0, scale: 0.96, y: 24 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.65, delay: 0.12 }}>
            <div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" />
            <GlassCard className="hero-case-card">
              <div className="mini-card-top"><span className="case-token">CASE #DL-2026-014</span><span className="live-dot">ANALYSIS READY</span></div>
              <h3>Property Dispute</h3><p>Ownership documents · 8 files</p>
              <div className="hero-progress"><span><i /> Evidence organized</span><strong>78%</strong></div>
              <div className="hero-progress-track"><span /></div>
              <div className="intelligence-row"><span><FileSearch size={15} /> 12 evidence items</span><span><BookOpen size={15} /> 3 references</span></div>
            </GlassCard>
            <div className="float-node node-document"><FileSearch size={18} /><span><small>DOCUMENT</small><strong>Extracted</strong></span></div>
            <div className="float-node node-evidence"><ShieldCheck size={18} /><span><small>EVIDENCE</small><strong>Verified</strong></span></div>
            <div className="float-node node-reference"><BookOpen size={18} /><span><small>REFERENCE</small><strong>Matched</strong></span></div>
            <div className="float-node node-action"><Sparkles size={18} /><span><small>AI ACTION</small><strong>Next step</strong></span></div>
            <svg className="hero-connections" viewBox="0 0 620 480" aria-hidden="true"><path d="M128 102 C180 145 180 175 228 194 M465 98 C426 142 420 158 390 194 M143 380 C192 335 206 327 242 312 M465 384 C430 347 416 333 384 315" /></svg>
          </motion.div>
        </section>

        <section className="landing-section" id="how-it-works">
          <div className="section-heading centered"><SectionLabel icon={Sparkles}>HOW DIGILAW HELPS</SectionLabel><h2>Clarity at every point in your legal journey.</h2><p>A calmer, more organized way to engage with the information around your case.</p></div>
          <div className="help-grid">{helpCards.map(({ icon: Icon, title, text }, index) => <motion.article className="help-card" key={title} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: index * 0.04 }}><span className="help-icon"><Icon size={20} /></span><h3>{title}</h3><p>{text}</p><span className="card-arrow"><ChevronRight size={17} /></span></motion.article>)}</div>
        </section>

        <section className="landing-section workflow-section">
          <GlassCard className="workflow-card">
            <div className="workflow-copy"><SectionLabel icon={FolderOpen}>DOCUMENT TO INTELLIGENCE</SectionLabel><h2>From documents to legal intelligence.</h2><p>Bring material together, make it reviewable, and understand what may need attention—inside one thoughtful workspace.</p><Link to="/register" className="text-arrow">Create a demo workspace <ArrowRight size={16} /></Link></div>
            <div className="workflow-steps">{['Upload', 'Extract', 'Analyze', 'Connect', 'Act'].map((step, index) => <div className="workflow-step" key={step}><span>0{index + 1}</span><strong>{step}</strong>{index < 4 ? <i><ArrowRight size={15} /></i> : null}</div>)}</div>
          </GlassCard>
        </section>

        <section className="landing-section workspace-section">
          <div className="section-heading"><SectionLabel icon={Scale}>ONE WORKSPACE</SectionLabel><h2>Built around your case,<br />not around busywork.</h2><p>Every case gets a connected space for evidence, documents, legal references, and structured review.</p></div>
          <div className="workspace-preview">
            <div className="preview-sidebar"><BrandMark /><span className="preview-nav-active">Overview</span><span>Documents</span><span>Evidence</span><span>Legal analysis</span><span>Action plan</span></div>
            <div className="preview-content"><div className="preview-title"><span><small>CASE NO. DL-2026-014</small><strong>Property Dispute</strong></span><BadgeLike>Analysis ready</BadgeLike></div><div className="preview-bars"><div><small>CASE PROGRESS</small><strong>78%</strong><span><i /></span></div><div><small>EVIDENCE STRENGTH</small><strong>Strong</strong><span><i /></span></div><div><small>DOCUMENTS</small><strong>8 of 10</strong><span><i /></span></div></div><div className="preview-insight"><Sparkles size={18} /><span><small>AI-ASSISTED INSIGHT</small><strong>Two documents may need review before the next step.</strong></span></div></div>
          </div>
        </section>

        <section className="landing-section responsible-section" id="responsible-ai">
          <div className="responsible-icon"><LockKeyhole size={26} /></div>
          <div><SectionLabel>RESPONSIBLE LEGAL UX</SectionLabel><h2>Intelligence to inform your review.</h2><p>DigiLaw is an AI-assisted information and organization platform. It is designed to make legal information easier to navigate, never to replace qualified legal advice.</p><div className="responsible-points"><span><Check size={16} /> Transparent AI-assisted labels</span><span><Check size={16} /> Verifiable reference context</span><span><Check size={16} /> Professional review encouraged</span></div></div>
        </section>

        <section className="final-cta">
          <SectionLabel icon={Sparkles}>YOUR WORKSPACE AWAITS</SectionLabel><h2>Bring calm, structure, and clarity<br />to your legal information.</h2><Link className="button button-primary" to="/register">Explore DigiLaw <ArrowRight size={17} /></Link>
        </section>
      </main>
      <footer className="marketing-footer"><BrandMark /><p>AI-powered legal intelligence for informed review.</p><p>© 2026 DigiLaw</p></footer>
    </div>
  )
}

function BadgeLike({ children }) {
  return <span className="badge badge-success">{children}</span>
}

function AuthShell({ children }) {
  return <div className="auth-page"><section className="auth-aside"><Link to="/"><BrandMark light /></Link><div className="auth-aside-copy"><SectionLabel icon={Sparkles}>DIGILAW WORKSPACE</SectionLabel><h1>Your legal information,<br /><em>organized intelligently.</em></h1><p>A secure-feeling demo workspace for evidence, documents, context, and meaningful next steps.</p></div><div className="auth-orb-visual"><div className="auth-orb-main"><Scale size={30} /><span>LAW<br />+ AI</span></div><div className="auth-orb-card card-one"><FileSearch size={17} /> Document review</div><div className="auth-orb-card card-two"><Sparkles size={17} /> AI-assisted insight</div></div><p className="auth-aside-footer">AI-assisted legal information and organization.</p></section><section className="auth-main"><Link className="auth-mobile-brand" to="/"><BrandMark /></Link><div className="auth-card-wrap">{children}</div></section></div>
}

function Field({ label, type = 'text', value, onChange, placeholder, error, autoComplete }) {
  return <label className="form-field"><span>{label}</span><input type={type} value={value} onChange={onChange} placeholder={placeholder} autoComplete={autoComplete} aria-invalid={Boolean(error)} />{error ? <small className="field-error">{error}</small> : null}</label>
}

export function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [values, setValues] = useState({ email: 'demo@digilaw.app', password: 'Demo123!' })
  const [error, setError] = useState('')
  function submit(event) {
    event.preventDefault()
    const result = login(values.email, values.password)
    if (!result.success) return setError(result.message)
    navigate('/dashboard')
  }
  return <AuthShell><div className="auth-form-head"><SectionLabel icon={Mail}>WELCOME BACK</SectionLabel><h2>Sign in to DigiLaw</h2><p>Continue to your legal intelligence workspace.</p></div><form className="auth-form" onSubmit={submit}><Field label="Email address" type="email" value={values.email} onChange={(event) => setValues({ ...values, email: event.target.value })} autoComplete="email" /><Field label="Password" type="password" value={values.password} onChange={(event) => setValues({ ...values, password: event.target.value })} autoComplete="current-password" />{error ? <p className="form-error">{error}</p> : null}<div className="form-options"><label className="checkbox"><input type="checkbox" defaultChecked /><span>Remember me</span></label><Link to="/forgot-password">Forgot password?</Link></div><Button type="submit" className="auth-submit" icon={ArrowRight}>Sign in</Button></form><div className="demo-credentials"><Sparkles size={16} /><span><strong>Demo access</strong><br />demo@digilaw.app &nbsp;·&nbsp; Demo123!</span></div><p className="auth-switch">Don&apos;t have an account? <Link to="/register">Create account</Link></p></AuthShell>
}

export function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [values, setValues] = useState({ name: '', email: '', password: '', confirm: '', phone: '', terms: false })
  const [errors, setErrors] = useState({})
  const strength = values.password.length > 10 ? 3 : values.password.length > 6 ? 2 : values.password.length ? 1 : 0
  function submit(event) {
    event.preventDefault()
    const nextErrors = {}
    if (!values.name.trim()) nextErrors.name = 'Enter your full name.'
    if (!/^\S+@\S+\.\S+$/.test(values.email)) nextErrors.email = 'Enter a valid email address.'
    if (values.password.length < 8) nextErrors.password = 'Use at least 8 characters.'
    if (values.password !== values.confirm) nextErrors.confirm = 'Passwords do not match.'
    if (!values.terms) nextErrors.terms = 'Please accept the terms to continue.'
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length) return
    register(values.name, values.email)
    navigate('/dashboard')
  }
  return <AuthShell><div className="auth-form-head"><SectionLabel icon={Sparkles}>CREATE YOUR WORKSPACE</SectionLabel><h2>Create a DigiLaw account</h2><p>Start with a secure-looking demo workspace. No backend account is created.</p></div><form className="auth-form" onSubmit={submit}><Field label="Full name" value={values.name} onChange={(event) => setValues({ ...values, name: event.target.value })} error={errors.name} autoComplete="name" /><Field label="Email address" type="email" value={values.email} onChange={(event) => setValues({ ...values, email: event.target.value })} error={errors.email} autoComplete="email" /><Field label="Phone (optional)" type="tel" value={values.phone} onChange={(event) => setValues({ ...values, phone: event.target.value })} autoComplete="tel" /><Field label="Password" type="password" value={values.password} onChange={(event) => setValues({ ...values, password: event.target.value })} error={errors.password} autoComplete="new-password" /><div className="password-strength"><div><span>Password strength</span><strong>{['', 'Fair', 'Good', 'Strong'][strength] || 'Add a password'}</strong></div><p>{[1, 2, 3].map((bar) => <i key={bar} className={bar <= strength ? 'is-active' : ''} />)}</p></div><Field label="Confirm password" type="password" value={values.confirm} onChange={(event) => setValues({ ...values, confirm: event.target.value })} error={errors.confirm} autoComplete="new-password" /><label className="checkbox terms-check"><input type="checkbox" checked={values.terms} onChange={(event) => setValues({ ...values, terms: event.target.checked })} /><span>I agree to the <a href="#terms">Terms</a> and <a href="#privacy">Privacy Policy</a>.</span></label>{errors.terms ? <p className="field-error">{errors.terms}</p> : null}<Button type="submit" className="auth-submit" icon={ArrowRight}>Create DigiLaw account</Button></form><p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p></AuthShell>
}

export function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  function submit(event) { event.preventDefault(); if (email) setSent(true) }
  return <AuthShell><div className="auth-form-head"><SectionLabel icon={LockKeyhole}>ACCOUNT RECOVERY</SectionLabel><h2>Reset your password</h2><p>Enter your email and we&apos;ll prepare a demo reset message.</p></div>{sent ? <div className="auth-success"><span><Check size={26} /></span><h3>Check your inbox</h3><p>A demo reset link has been prepared for <strong>{email}</strong>. No email was actually sent.</p><Link className="button button-secondary" to="/login">Return to sign in</Link></div> : <form className="auth-form" onSubmit={submit}><Field label="Email address" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" autoComplete="email" /><Button type="submit" className="auth-submit" icon={ArrowRight}>Send reset link</Button></form>}<p className="auth-switch"><Link to="/login">Back to sign in</Link></p></AuthShell>
}
