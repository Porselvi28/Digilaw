import { AnimatePresence, motion } from 'framer-motion'
import {
  Bell, BookOpen, BriefcaseBusiness, FileText, LayoutDashboard, LogOut, Menu,
  MessageSquare, Network, PanelLeftClose, Scale, Settings, ShieldCheck, Sparkles,
  X, ListChecks,
} from 'lucide-react'
import { NavLink, Navigate, Outlet, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../context/auth'
import { cn } from '../utils/classNames'

const navigation = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'My Cases', to: '/cases', icon: BriefcaseBusiness },
  { label: 'Evidence', to: '/cases/DL-2026-014/evidence', icon: ShieldCheck },
  { label: 'Documents', to: '/cases/DL-2026-014/documents', icon: FileText },
  { label: 'Legal Analysis', to: '/cases/DL-2026-014/analysis', icon: Network },
  { label: 'Similar Cases', to: '/cases/DL-2026-014/similar-cases', icon: BookOpen },
  { label: 'Action Plans', to: '/cases/DL-2026-014/action-plan', icon: ListChecks },
  { label: 'Ask DigiLaw', to: '/ask-legal', icon: MessageSquare },
]

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/cases': 'My Cases',
  '/ask-legal': 'Ask DigiLaw',
  '/notifications': 'Notifications',
  '/settings': 'Settings',
  '/profile': 'Profile',
}

export function BrandMark({ light = false }) {
  return (
    <span className={cn('brand-mark', light && 'brand-mark-light')}>
      <span className="brand-emblem"><Scale size={17} aria-hidden="true" /></span>
      <span><strong>DigiLaw</strong><small>LEGAL INTELLIGENCE</small></span>
    </span>
  )
}

function Sidebar({ open, onClose, collapsed, onToggle }) {
  const { user, logout } = useAuth()
  return (
    <aside className={cn('sidebar', open && 'sidebar-open', collapsed && 'sidebar-collapsed')}>
      <div className="sidebar-top">
        <NavLink to="/dashboard" className="brand-link" aria-label="DigiLaw dashboard"><BrandMark /></NavLink>
        <button className="sidebar-toggle icon-button" onClick={onToggle} aria-label="Collapse navigation"><PanelLeftClose size={18} /></button>
        <button className="sidebar-close icon-button" onClick={onClose} aria-label="Close navigation"><X size={19} /></button>
      </div>
      <nav className="side-nav" aria-label="Primary navigation">
        <p className="nav-group-label">Workspace</p>
        {navigation.map(({ label, to, icon: Icon }) => (
          <NavLink key={label} to={to} end={to === '/cases'} className={({ isActive }) => cn('nav-item', isActive && 'nav-active')} onClick={onClose}>
            <Icon size={18} strokeWidth={1.8} aria-hidden="true" />
            <span>{label}</span>
            {label === 'Ask DigiLaw' ? <Sparkles className="nav-sparkle" size={14} aria-hidden="true" /> : null}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <NavLink to="/notifications" className={({ isActive }) => cn('nav-item', isActive && 'nav-active')} onClick={onClose}><Bell size={18} /><span>Notifications</span><i className="notice-dot" /></NavLink>
        <NavLink to="/settings" className={({ isActive }) => cn('nav-item', isActive && 'nav-active')} onClick={onClose}><Settings size={18} /><span>Settings</span></NavLink>
        <div className="profile-row">
          <NavLink to="/profile" className="profile-mini" onClick={onClose}>
            <span className="avatar">{user?.initials || 'AM'}</span>
            <span><strong>{user?.name || 'Demo user'}</strong><small>{user?.role || 'Demo access'}</small></span>
          </NavLink>
          <button className="icon-button logout-button" onClick={logout} aria-label="Sign out"><LogOut size={16} /></button>
        </div>
      </div>
    </aside>
  )
}

function TopBar({ onMenu }) {
  const location = useLocation()
  const title = pageTitles[location.pathname] || (location.pathname.includes('/cases/') ? 'Case Workspace' : 'DigiLaw')
  return (
    <header className="topbar">
      <button className="mobile-menu icon-button" onClick={onMenu} aria-label="Open navigation"><Menu size={21} /></button>
      <div className="crumb"><span>Workspace</span><b>/</b><strong>{title}</strong></div>
      <div className="top-actions">
        <span className="system-ready"><i />AI system ready</span>
        <NavLink to="/notifications" className="icon-button notification-button" aria-label="Notifications"><Bell size={19} /><i className="notice-dot" /></NavLink>
        <NavLink to="/profile" className="avatar top-avatar" aria-label="Open profile">AM</NavLink>
      </div>
    </header>
  )
}

function MobileNav() {
  return (
    <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
      {navigation.slice(0, 4).map(({ label, to, icon: Icon }) => (
        <NavLink key={label} to={to} end={to === '/cases'}><Icon size={18} /><span>{label.replace('My ', '')}</span></NavLink>
      ))}
    </nav>
  )
}

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  return (
    <div className={cn('app-shell', collapsed && 'app-shell-collapsed')}>
      <AnimatePresence>{mobileOpen ? <motion.div className="sidebar-scrim" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setMobileOpen(false)} /> : null}</AnimatePresence>
      <Sidebar open={mobileOpen} onClose={() => setMobileOpen(false)} collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
      <div className="app-main">
        <TopBar onMenu={() => setMobileOpen(true)} />
        <main className="page-content"><Outlet /></main>
      </div>
      <MobileNav />
    </div>
  )
}

export function ProtectedRoute() {
  const { user } = useAuth()
  return user ? <Outlet /> : <Navigate to="/login" replace />
}
