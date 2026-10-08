import { AnimatePresence, motion } from 'framer-motion'
import { ArrowRight, Search, Sparkles, X } from 'lucide-react'
import { cn } from '../utils/classNames'

export function Button({ children, className, variant = 'primary', icon: Icon, type = 'button', ...props }) {
  return (
    <motion.button
      type={type}
      className={cn('button', 'button-' + variant, className)}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.15 }}
      {...props}
    >
      {children}
      {Icon ? <Icon size={16} strokeWidth={2.25} aria-hidden="true" /> : null}
    </motion.button>
  )
}

export function GlassCard({ children, className, as: Tag = 'section', ...props }) {
  return <Tag className={cn('glass-card', className)} {...props}>{children}</Tag>
}

export function Badge({ children, tone = 'neutral', className }) {
  return <span className={cn('badge', 'badge-' + tone, className)}>{children}</span>
}

export function SectionLabel({ children, icon: Icon, className }) {
  return <p className={cn('section-label', className)}>{Icon ? <Icon size={13} aria-hidden="true" /> : null}{children}</p>
}

export function ProgressBar({ value, label, className }) {
  return (
    <div className={cn('progress-wrap', className)}>
      {label ? <div className="progress-label"><span>{label}</span><strong>{value}%</strong></div> : null}
      <div className="progress-track" role="progressbar" aria-valuenow={value} aria-valuemin="0" aria-valuemax="100">
        <motion.span className="progress-fill" initial={{ width: 0 }} animate={{ width: value + '%' }} transition={{ duration: 0.75, ease: 'easeOut' }} />
      </div>
    </div>
  )
}

export function ProgressRing({ value, label, detail, size = 'medium' }) {
  return (
    <div className={cn('progress-ring', 'progress-ring-' + size)} style={{ '--progress': value + '%' }}>
      <div className="progress-ring-inner">
        <strong>{value}%</strong>
        {label ? <span>{label}</span> : null}
      </div>
      {detail ? <span className="ring-detail">{detail}</span> : null}
    </div>
  )
}

export function SearchInput({ value, onChange, placeholder = 'Search', className }) {
  return (
    <label className={cn('search-input', className)}>
      <Search size={17} aria-hidden="true" />
      <input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} aria-label={placeholder} />
    </label>
  )
}

export function EmptyState({ title, detail, action, icon: Icon = Sparkles }) {
  return (
    <GlassCard className="empty-state">
      <span className="empty-icon"><Icon size={24} aria-hidden="true" /></span>
      <h3>{title}</h3>
      <p>{detail}</p>
      {action}
    </GlassCard>
  )
}

export function Skeleton({ className }) {
  return <span className={cn('skeleton', className)} aria-hidden="true" />
}

export function Modal({ open, onClose, title, children, wide = false }) {
  return (
    <AnimatePresence>
      {open ? (
        <motion.div className="modal-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={onClose}>
          <motion.div
            className={cn('modal-panel', wide && 'modal-wide')}
            initial={{ opacity: 0, scale: 0.96, y: 14 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 14 }}
            transition={{ duration: 0.22 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <h2 id="modal-title">{title}</h2>
              <button className="icon-button" onClick={onClose} aria-label="Close dialog"><X size={19} /></button>
            </div>
            {children}
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}

export function PageIntro({ eyebrow, title, description, action }) {
  return (
    <div className="page-intro">
      <div>
        {eyebrow ? <SectionLabel icon={Sparkles}>{eyebrow}</SectionLabel> : null}
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      {action}
    </div>
  )
}

export function TextLink({ children, className, onClick }) {
  return <button className={cn('text-link', className)} onClick={onClick}>{children}<ArrowRight size={15} /></button>
}

export function Disclaimer({ compact = false }) {
  return <p className={cn('disclaimer', compact && 'disclaimer-compact')}><Sparkles size={14} aria-hidden="true" />AI-assisted information for organization and review—not legal advice. Verify important matters with a qualified legal professional.</p>
}
