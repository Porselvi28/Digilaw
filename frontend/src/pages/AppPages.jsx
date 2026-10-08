import { motion } from 'framer-motion'
import {
  AlertTriangle, ArrowRight, Bell, BookOpen, Brain, BriefcaseBusiness,
  Check, CheckCircle2, ChevronRight, CircleAlert, Download,
  Eye, FileImage, FilePlus2, FileText, Filter, FolderOpen,
  Grid2X2, LayoutList, ListChecks, MapPin, MessageSquare, MoreHorizontal,
  Paperclip, Plus, Scale, Send, Settings2, ShieldCheck, SlidersHorizontal,
  Sparkles, Upload, UserRound,
} from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useState } from 'react'
import {
  actionPlan, analysisStages, dashboardMetrics, documents, evidenceItems, initialConversation,
  legalReferences, notifications, similarCases,
} from '../data/mockData'
import { useDemoData } from '../context/demo'
import { Badge, Button, Disclaimer, EmptyState, GlassCard, Modal, PageIntro, ProgressBar, ProgressRing, SearchInput, SectionLabel } from '../components/ui'

const iconMap = { briefcase: BriefcaseBusiness, file: FileText, shield: ShieldCheck, checklist: ListChecks }

function Page({ children, className = '' }) {
  return <motion.div className={'app-page ' + className} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>{children}</motion.div>
}

function CaseStatus({ caseItem }) {
  return <Badge tone={caseItem.tone}>{caseItem.status}</Badge>
}

function CaseCard({ caseItem, list = false }) {
  return (
    <motion.article className={'case-card ' + (list ? 'case-card-list' : '')} whileHover={{ y: -3 }} transition={{ duration: 0.18 }}>
      <div className="case-card-top"><span className="case-number">CASE #{caseItem.id}</span><CaseStatus caseItem={caseItem} /><button className="icon-button quiet-more" aria-label={'More options for ' + caseItem.title}><MoreHorizontal size={18} /></button></div>
      <div className="case-card-heading"><span className="case-icon"><BriefcaseBusiness size={19} /></span><div><h3>{caseItem.title}</h3><p>{caseItem.category} · {caseItem.jurisdiction}</p></div></div>
      <div className="case-details"><span><strong>{caseItem.evidence}</strong> evidence</span><span><strong>{caseItem.documents}</strong> documents</span><span>Updated {caseItem.updatedAt}</span></div>
      <ProgressBar value={caseItem.progress} label="Case progress" />
      <div className="case-card-footer"><span><Sparkles size={14} />{caseItem.nextAction}</span><Link to={'/cases/' + caseItem.id}>Open case <ArrowRight size={15} /></Link></div>
    </motion.article>
  )
}

function CurrentCase({ children }) {
  const { caseId } = useParams()
  const { cases } = useDemoData()
  const activeCase = cases.find((item) => item.id === caseId) || cases[0]
  return children(activeCase)
}

function CaseTabNav({ caseId, active }) {
  const tabs = [
    ['Overview', '/cases/' + caseId],
    ['Documents', '/cases/' + caseId + '/documents'],
    ['Evidence', '/cases/' + caseId + '/evidence'],
    ['Legal Analysis', '/cases/' + caseId + '/analysis'],
    ['Similar Cases', '/cases/' + caseId + '/similar-cases'],
    ['Action Plan', '/cases/' + caseId + '/action-plan'],
  ]
  return <nav className="case-tab-nav" aria-label="Case navigation">{tabs.map(([label, to]) => <Link key={label} to={to} className={active === label ? 'case-tab-active' : ''}>{label}</Link>)}</nav>
}

export function Dashboard() {
  const { cases } = useDemoData()
  const current = cases[0]
  return <Page>
    <PageIntro eyebrow="YOUR LEGAL INTELLIGENCE" title="Good morning, Aarav." description="Here is your legal intelligence overview." action={<span className="system-ready intro-ready"><i /> AI system ready</span>} />
    <section className="metrics-grid">{dashboardMetrics.map((metric, index) => { const Icon = iconMap[metric.icon]; return <motion.div className={'metric-card metric-' + metric.tone} key={metric.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}><span className="metric-icon"><Icon size={19} /></span><div><small>{metric.label}</small><strong>{metric.value}</strong><p>{metric.detail}</p></div></motion.div> })}</section>
    <section className="dashboard-grid">
      <GlassCard className="intelligence-overview">
        <div className="panel-head"><div><SectionLabel icon={Sparkles}>CASE INTELLIGENCE OVERVIEW</SectionLabel><h2>{current.title}</h2><p>CASE #{current.id} · {current.category}</p></div><CaseStatus caseItem={current} /></div>
        <div className="overview-content"><div className="overview-progress"><ProgressRing value={current.progress} label="case ready" size="large" /><div><h3>Structured review is ready.</h3><p>Evidence and document materials are organized for the next stage of review.</p><Link className="button button-primary" to={'/cases/' + current.id + '/analysis'}>Continue analysis <ArrowRight size={16} /></Link></div></div><div className="overview-stats"><span><small>EVIDENCE STRENGTH</small><strong>78%</strong><i className="status-positive">Strong</i></span><span><small>DOCUMENT COMPLETENESS</small><strong>65%</strong><i className="status-warning">Review needed</i></span><span><small>NEXT REVIEW</small><strong>2</strong><i>items flagged</i></span></div></div>
      </GlassCard>
      <GlassCard className="insights-panel"><div className="panel-head"><div><SectionLabel icon={Brain}>AI LEGAL INSIGHTS</SectionLabel><h2>Assessment signals</h2></div><Badge tone="purple">AI-assisted</Badge></div><div className="insight-rings"><ProgressRing value={87} label="Legal relevance" /><ProgressRing value={78} label="Evidence strength" /><ProgressRing value={65} label="Document completeness" /><ProgressRing value={82} label="Similar case confidence" /></div><Disclaimer compact /></GlassCard>
    </section>
    <section className="dashboard-bottom">
      <GlassCard className="recent-documents"><div className="panel-head"><div><SectionLabel icon={FileText}>RECENT DOCUMENTS</SectionLabel><h2>Keep the record in view</h2></div><Link className="small-link" to={'/cases/' + current.id + '/documents'}>View all <ArrowRight size={15} /></Link></div><div className="document-list">{documents.slice(0, 4).map((document) => <div className="document-list-item" key={document.id}><span className="doc-icon"><FileText size={18} /></span><div><strong>{document.name}</strong><small>{document.kind} · {document.uploaded}</small></div><Badge tone={document.tone}>{document.status}</Badge></div>)}</div></GlassCard>
      <GlassCard className="reference-panel"><div className="panel-head"><div><SectionLabel icon={BookOpen}>LEGAL REFERENCES</SectionLabel><h2>Relevant material for review</h2></div><Link className="small-link" to={'/cases/' + current.id + '/analysis'}>Explore <ArrowRight size={15} /></Link></div><div className="reference-list">{legalReferences.slice(0, 2).map((reference) => <article key={reference.id}><span className={'reference-dot dot-' + reference.tone} /><div><small>{reference.relevance}</small><h3>{reference.title}</h3><p>{reference.section}</p></div><ChevronRight size={18} /></article>)}</div><Disclaimer compact /></GlassCard>
    </section>
  </Page>
}

function CreateCaseModal({ open, onClose }) {
  const { createCase } = useDemoData()
  const [values, setValues] = useState({ title: '', type: 'Property', description: '', jurisdiction: '', date: '', notes: '' })
  const navigate = useNavigate()
  function submit(event) { event.preventDefault(); if (!values.title || !values.description) return; const newCase = createCase(values); onClose(); navigate('/cases/' + newCase.id) }
  return <Modal open={open} onClose={onClose} title="Create a new case"><p className="modal-subtitle">This creates a case in temporary demo state only.</p><form className="case-form" onSubmit={submit}><label className="form-field"><span>Case title</span><input value={values.title} onChange={(event) => setValues({ ...values, title: event.target.value })} placeholder="e.g. Property ownership review" required /></label><div className="form-grid"><label className="form-field"><span>Case type</span><select value={values.type} onChange={(event) => setValues({ ...values, type: event.target.value })}>{['Property', 'Consumer', 'Employment', 'Education / Ragging', 'Family', 'Cyber / Online', 'Other'].map((item) => <option key={item}>{item}</option>)}</select></label><label className="form-field"><span>Jurisdiction</span><input value={values.jurisdiction} onChange={(event) => setValues({ ...values, jurisdiction: event.target.value })} placeholder="City, State" /></label></div><label className="form-field"><span>Description</span><textarea value={values.description} onChange={(event) => setValues({ ...values, description: event.target.value })} placeholder="Briefly describe the information you want to organize." required /></label><div className="form-grid"><label className="form-field"><span>Relevant date</span><input type="date" value={values.date} onChange={(event) => setValues({ ...values, date: event.target.value })} /></label><label className="form-field"><span>Optional notes</span><input value={values.notes} onChange={(event) => setValues({ ...values, notes: event.target.value })} placeholder="Anything else to note" /></label></div><div className="modal-actions"><Button variant="secondary" onClick={onClose}>Cancel</Button><Button type="submit" icon={ArrowRight}>Create demo case</Button></div></form></Modal>
}

export function Cases() {
  const { cases } = useDemoData()
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('All')
  const [view, setView] = useState('grid')
  const [createOpen, setCreateOpen] = useState(false)
  const filtered = cases.filter((item) => (filter === 'All' || item.status.includes(filter) || item.tone === filter.toLowerCase()) && (item.title + item.category + item.id).toLowerCase().includes(query.toLowerCase()))
  const filters = ['All', 'Active', 'Analysis', 'Action Required', 'Completed']
  return <Page><PageIntro eyebrow="CASE MANAGEMENT" title="My Cases" description="Manage and explore your legal matters." action={<Button icon={Plus} onClick={() => setCreateOpen(true)}>Create new case</Button>} /><div className="case-controls"><SearchInput value={query} onChange={setQuery} placeholder="Search cases, types, or case number" /><div className="filter-pills" role="group" aria-label="Filter cases">{filters.map((item) => <button key={item} className={filter === item ? 'pill-active' : ''} onClick={() => setFilter(item)}>{item}</button>)}</div><div className="view-toggle"><button className={view === 'grid' ? 'toggle-active' : ''} onClick={() => setView('grid')} aria-label="Grid view"><Grid2X2 size={17} /></button><button className={view === 'list' ? 'toggle-active' : ''} onClick={() => setView('list')} aria-label="List view"><LayoutList size={17} /></button></div></div>{filtered.length ? <div className={'cases-layout cases-' + view}>{filtered.map((caseItem) => <CaseCard key={caseItem.id} caseItem={caseItem} list={view === 'list'} />)}</div> : <EmptyState title="No cases matched your search" detail="Try changing the filter or add a new demo case." action={<Button icon={Plus} onClick={() => setCreateOpen(true)}>Create your first case</Button>} icon={FolderOpen} />}<CreateCaseModal open={createOpen} onClose={() => setCreateOpen(false)} /></Page>
}

export function CaseWorkspace() {
  return <CurrentCase>{(activeCase) => <Page className="case-workspace-page"><div className="case-workspace-head"><div><Link className="back-link" to="/cases">My cases</Link><SectionLabel icon={BriefcaseBusiness}>CASE #{activeCase.id}</SectionLabel><h1>{activeCase.title}</h1><p>{activeCase.category} · <MapPin size={14} /> {activeCase.jurisdiction}</p></div><div className="workspace-head-actions"><CaseStatus caseItem={activeCase} /><Button icon={ArrowRight}>Continue analysis</Button></div></div><CaseTabNav caseId={activeCase.id} active="Overview" /><div className="workspace-overview"><GlassCard className="case-summary-card"><div className="case-summary-head"><div><SectionLabel>CASE OVERVIEW</SectionLabel><h2>Case intelligence at a glance</h2></div><span className="case-icon large"><BriefcaseBusiness size={22} /></span></div><p>{activeCase.description}</p><dl className="case-meta-grid"><div><dt>CASE TYPE</dt><dd>{activeCase.category}</dd></div><div><dt>JURISDICTION</dt><dd>{activeCase.jurisdiction}</dd></div><div><dt>CREATED</dt><dd>{activeCase.createdAt}</dd></div><div><dt>LAST UPDATED</dt><dd>{activeCase.updatedAt}</dd></div></dl></GlassCard><GlassCard className="case-progress-card"><SectionLabel icon={Sparkles}>CASE PROGRESS</SectionLabel><ProgressRing value={activeCase.progress} label="ready for review" size="large" /><div><ProgressBar value={78} label="Evidence completeness" /><ProgressBar value={65} label="Document completeness" /><ProgressBar value={82} label="AI analysis status" /></div></GlassCard><GlassCard className="next-step-card"><SectionLabel icon={ArrowRight}>NEXT RECOMMENDED STEP</SectionLabel><h2>{activeCase.nextAction}</h2><p>Review flagged items, verify available information, and keep the case record complete before progressing.</p><Link className="button button-secondary" to={'/cases/' + activeCase.id + '/documents'}>Review documents <ArrowRight size={16} /></Link></GlassCard></div><div className="workspace-lower"><GlassCard><div className="panel-head"><div><SectionLabel icon={ShieldCheck}>EVIDENCE SUMMARY</SectionLabel><h2>Structured evidence</h2></div><Link className="small-link" to={'/cases/' + activeCase.id + '/evidence'}>View evidence <ArrowRight size={15} /></Link></div><div className="mini-stat-row"><span><strong>{activeCase.evidence}</strong><small>Evidence items</small></span><span><strong>9</strong><small>Verified</small></span><span><strong>2</strong><small>Needs review</small></span></div></GlassCard><GlassCard><div className="panel-head"><div><SectionLabel icon={BookOpen}>LEGAL REFERENCES</SectionLabel><h2>Context for review</h2></div><Badge tone="purple">AI-assisted</Badge></div><p className="short-panel-text">Potentially relevant legal material is organized here as reference context, ready for professional verification.</p><Disclaimer compact /></GlassCard></div></Page>}</CurrentCase>
}

function WorkspacePageHeader({ active, title, description, children }) {
  return <CurrentCase>{(activeCase) => <><div className="case-page-head"><div><Link className="back-link" to={'/cases/' + activeCase.id}>CASE #{activeCase.id}</Link><h1>{title}</h1><p>{description}</p></div>{children}</div><CaseTabNav caseId={activeCase.id} active={active} /></>}</CurrentCase>
}

export function DocumentsPage() {
  const { caseId } = useParams()
  const [dragging, setDragging] = useState(false)
  const [selected, setSelected] = useState(null)
  const [query, setQuery] = useState('')
  const caseDocuments = documents.filter((item) => item.caseId === caseId).filter((item) => item.name.toLowerCase().includes(query.toLowerCase()))
  return <Page><WorkspacePageHeader active="Documents" title="Documents" description="Organize the documents that support your case."><Button icon={Upload} onClick={() => document.getElementById('document-input').click()}>Upload document</Button></WorkspacePageHeader><input id="document-input" type="file" hidden onChange={(event) => setSelected(event.target.files?.[0])} /><section className="document-toolbar"><SearchInput value={query} onChange={setQuery} placeholder="Search documents" /><button className="filter-button"><Filter size={16} /> Filter</button><button className="filter-button"><SlidersHorizontal size={16} /> Sort</button></section><div className={'upload-zone ' + (dragging ? 'upload-dragging' : '')} onDragOver={(event) => { event.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); setSelected(event.dataTransfer.files[0]) }} onClick={() => document.getElementById('document-input').click()} role="button" tabIndex="0" onKeyDown={(event) => event.key === 'Enter' && document.getElementById('document-input').click()}><span><Upload size={24} /></span><div><h3>{selected ? selected.name : 'Drop legal documents here'}</h3><p>{selected ? ((selected.size / 1024 / 1024).toFixed(2) + ' MB · ready for demo processing') : 'PDF, DOCX, JPG, PNG · up to 10 MB'}</p></div>{selected ? <Badge tone="info">Ready to upload</Badge> : <Button variant="secondary" icon={FilePlus2}>Choose file</Button>}</div><GlassCard className="document-table-card"><div className="document-table">{caseDocuments.map((document) => <article key={document.id}><span className="doc-icon"><FileText size={19} /></span><div className="document-name"><strong>{document.name}</strong><small>{document.kind} · {document.size}</small></div><span className="table-muted">{document.uploaded}</span><Badge tone={document.tone}>{document.status}</Badge><div className="table-actions"><button className="icon-button" aria-label={'Preview ' + document.name}><Eye size={17} /></button><button className="icon-button" aria-label={'More options for ' + document.name}><MoreHorizontal size={17} /></button></div></article>)}</div>{!caseDocuments.length ? <EmptyState title="No documents found" detail="Adjust the search or upload a document to begin." icon={FileText} /> : null}</GlassCard><Disclaimer /></Page>
}

export function EvidencePage() {
  const { caseId } = useParams()
  const caseEvidence = evidenceItems.filter((item) => item.caseId === caseId)
  return <Page><WorkspacePageHeader active="Evidence" title="Evidence" description="Review and organize the material that supports your case."><Button icon={Plus}>Add evidence</Button></WorkspacePageHeader><section className="evidence-summary"><GlassCard><span className="summary-icon purple"><ShieldCheck size={19} /></span><div><small>EVIDENCE COUNT</small><strong>{caseEvidence.length || 0}</strong><p>Items linked to this case</p></div></GlassCard><GlassCard><span className="summary-icon green"><CheckCircle2 size={19} /></span><div><small>VERIFIED</small><strong>02</strong><p>Ready for human review</p></div></GlassCard><GlassCard><span className="summary-icon gold"><AlertTriangle size={19} /></span><div><small>NEEDS REVIEW</small><strong>01</strong><p>Requires clarification</p></div></GlassCard><GlassCard><span className="summary-icon muted"><FileImage size={19} /></span><div><small>UNCLASSIFIED</small><strong>01</strong><p>Awaiting categorization</p></div></GlassCard></section><section className="evidence-layout"><div className="evidence-list">{caseEvidence.length ? caseEvidence.map((evidence) => <GlassCard className="evidence-card" key={evidence.id}><div className="evidence-card-head"><span className="evidence-id">{evidence.id}</span><Badge tone={evidence.tone}>{evidence.status}</Badge></div><div className="evidence-card-body"><span className="evidence-icon"><ShieldCheck size={19} /></span><div><h3>{evidence.title}</h3><p>{evidence.description}</p></div></div><dl><div><dt>TYPE</dt><dd>{evidence.type}</dd></div><div><dt>SOURCE</dt><dd>{evidence.source}</dd></div><div><dt>DATE</dt><dd>{evidence.date}</dd></div><div><dt>RELEVANCE</dt><dd>{evidence.relevance}</dd></div></dl><button className="text-link">Open evidence <ArrowRight size={15} /></button></GlassCard>) : <EmptyState title="No evidence added yet" detail="Add a document or create an evidence item to start organizing the record." action={<Button icon={Plus}>Add evidence</Button>} icon={ShieldCheck} />}</div><GlassCard className="evidence-side-note"><SectionLabel icon={Sparkles}>EVIDENCE REVIEW</SectionLabel><h2>Keep the record verifiable.</h2><p>Classify source material, preserve context, and verify important facts before relying on them.</p><div className="evidence-checklist"><span><Check size={15} /> Identify the original source</span><span><Check size={15} /> Confirm dates and names</span><span><Check size={15} /> Note items requiring review</span></div><Disclaimer compact /></GlassCard></section></Page>
}

export function AnalysisPage() {
  return <Page><WorkspacePageHeader active="Legal Analysis" title="Legal Analysis" description="A structured, AI-assisted view of the information in this case."><Badge tone="info">Analysis in progress</Badge></WorkspacePageHeader><section className="analysis-layout"><GlassCard className="analysis-stages"><div className="panel-head"><div><SectionLabel icon={Brain}>PROCESSING STAGES</SectionLabel><h2>Analysis pipeline</h2></div><span className="processing-pulse"><i /> Processing</span></div><ol>{analysisStages.map((stage, index) => <li key={stage.title} className={'stage-' + stage.state}><span>{stage.state === 'complete' ? <Check size={15} /> : String(index + 1).padStart(2, '0')}</span><div><h3>{stage.title}</h3><p>{stage.detail}</p></div>{stage.state === 'active' ? <i className="stage-loader" /> : null}</li>)}</ol></GlassCard><div className="analysis-results"><GlassCard><SectionLabel icon={Sparkles}>AI-ASSISTED INSIGHT</SectionLabel><h2>Case summary</h2><p>Available materials indicate a document-led property matter. The current workspace contains ownership records, tax receipts, and correspondence that should be verified together.</p><div className="analysis-key-grid"><div><small>KEY INFORMATION</small><span><CheckCircle2 size={15} /> Ownership record identified</span><span><CheckCircle2 size={15} /> Timeline information found</span></div><div><small>MISSING INFORMATION</small><span><CircleAlert size={15} /> Prior transfer record</span><span><CircleAlert size={15} /> Full correspondence sequence</span></div></div></GlassCard><GlassCard><div className="panel-head"><div><SectionLabel icon={BookOpen}>POTENTIALLY RELEVANT REFERENCES</SectionLabel><h2>Reference for review</h2></div><Badge tone="purple">Verify context</Badge></div>{legalReferences.map((reference) => <article className="analysis-reference" key={reference.id}><span><BookOpen size={17} /></span><div><small>{reference.type}</small><h3>{reference.title} · {reference.section}</h3><p>{reference.summary}</p></div><ChevronRight size={17} /></article>)}</GlassCard><GlassCard><SectionLabel icon={MessageSquare}>QUESTIONS TO CLARIFY</SectionLabel><h2>Before progressing</h2><ul className="question-list"><li>Is the full ownership transfer chain available for review?</li><li>Have all parties and relevant dates been confirmed from original records?</li><li>Which details should be reviewed by a qualified legal professional?</li></ul><Disclaimer /></GlassCard></div></section></Page>
}

export function SimilarCasesPage() {
  return <Page><WorkspacePageHeader active="Similar Cases" title="Similar Cases" description="Comparable patterns from available reference material, surfaced for review."><Badge tone="purple">AI-assisted matching</Badge></WorkspacePageHeader><div className="similar-intro"><Sparkles size={19} /><span>Similarity indicates a pattern in the available material. It does not indicate a controlling precedent or predict an outcome.</span></div><section className="similar-grid">{similarCases.map((item, index) => <GlassCard className="similar-card" key={item.id}><div className="similar-card-top"><span className="similar-number">SIMILAR CASE #{index + 1}</span><ProgressRing value={item.similarity} label="similarity" /></div><h2>{item.title}</h2><p>{item.note}</p><dl><div><dt>CASE TYPE</dt><dd>{item.type}</dd></div><div><dt>KEY SIMILARITY</dt><dd>{item.issue}</dd></div><div><dt>REFERENCE</dt><dd>{item.metadata}</dd></div></dl><button className="text-link">Explore reference <ArrowRight size={15} /></button></GlassCard>)}</section><Disclaimer /></Page>
}

export function ActionPlanPage() {
  return <Page><WorkspacePageHeader active="Action Plan" title="Your Legal Action Plan" description="A careful, ordered checklist based on the current demo workspace."><Button variant="secondary" icon={Download}>Export plan</Button></WorkspacePageHeader><div className="action-intro"><div><SectionLabel icon={Sparkles}>AI-ASSISTED GUIDANCE</SectionLabel><h2>Organize what to review next.</h2></div><Disclaimer compact /></div><section className="action-timeline">{actionPlan.map((step) => <motion.article className="action-step" key={step.order} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: Number(step.order) * 0.06 }}><div className={'timeline-number timeline-' + step.tone}>{step.order}</div><GlassCard><div className="action-step-head"><div><Badge tone={step.tone}>{step.status}</Badge><span className={'priority priority-' + step.priority.toLowerCase()}>{step.priority} priority</span></div><button className="icon-button" aria-label={'More options for ' + step.title}><MoreHorizontal size={18} /></button></div><h2>{step.title}</h2><p>{step.description}</p><div className="action-docs"><FileText size={15} /><span><small>RELATED DOCUMENTS</small>{step.documents}</span></div></GlassCard></motion.article>)}</section><Disclaimer /></Page>
}

export function AskLegal() {
  const [messages, setMessages] = useState(initialConversation)
  const [draft, setDraft] = useState('')
  const questions = ['What documents are missing from my case?', 'Summarize the evidence in this case.', 'What information should I verify?', 'What legal references may be relevant?', 'What should I consider doing next?']
  function send(text) {
    const value = (text || draft).trim()
    if (!value) return
    setMessages((current) => [...current, { id: Date.now(), role: 'user', text: value, time: 'Now' }, { id: Date.now() + 1, role: 'assistant', text: 'For this demo workspace, DigiLaw would organize the relevant case information and point to materials that may need review. Please verify factual details and consult a qualified professional for important legal decisions.', time: 'Now', sources: ['Demo legal intelligence workspace'] }])
    setDraft('')
  }
  return <Page className="ask-page"><PageIntro eyebrow="AI-ASSISTED LEGAL INTELLIGENCE" title="Ask DigiLaw" description="Explore your case, documents, evidence, and legal information." action={<Badge tone="purple">Demo conversation</Badge>} /><section className="ask-layout"><GlassCard className="ask-context"><SectionLabel icon={BriefcaseBusiness}>CURRENT CONTEXT</SectionLabel><h2>Property Dispute</h2><p>CASE #DL-2026-014</p><div><span><FileText size={15} />8 documents</span><span><ShieldCheck size={15} />12 evidence items</span><span><BookOpen size={15} />3 references</span></div><hr /><SectionLabel icon={Sparkles}>SUGGESTED QUESTIONS</SectionLabel>{questions.map((question) => <button key={question} onClick={() => send(question)}>{question}<ChevronRight size={15} /></button>)}</GlassCard><GlassCard className="conversation-card"><div className="conversation-head"><div><span className="conversation-orb"><Sparkles size={17} /></span><div><h2>DigiLaw intelligence</h2><p><i /> AI-assisted information</p></div></div><span className="case-token">CASE #DL-2026-014</span></div><div className="message-list">{messages.map((message) => <article className={'message message-' + message.role} key={message.id}>{message.role === 'assistant' ? <span className="message-avatar"><Sparkles size={15} /></span> : <span className="avatar">AM</span>}<div><p>{message.text}</p>{message.sources ? <div className="message-sources">{message.sources.map((source) => <span key={source}><BookOpen size={12} />{source}</span>)}</div> : null}<small>{message.time}</small></div></article>)}</div><form className="chat-composer" onSubmit={(event) => { event.preventDefault(); send() }}><button className="icon-button" type="button" aria-label="Attach a document"><Paperclip size={18} /></button><input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Ask about your case or documents..." aria-label="Ask DigiLaw" /><Button type="submit" icon={Send}>Send</Button></form><Disclaimer compact /></GlassCard></section></Page>
}

export function NotificationsPage() {
  const iconByType = { file: FileText, sparkles: Sparkles, alert: AlertTriangle, checklist: ListChecks }
  return <Page><PageIntro eyebrow="WORKSPACE UPDATES" title="Notifications" description="Stay in sync with case activity and review items." action={<Button variant="secondary">Mark all as read</Button>} /><GlassCard className="notifications-card">{notifications.map((item) => { const Icon = iconByType[item.icon]; return <article className={'notification-item ' + (item.unread ? 'notification-unread' : '')} key={item.id}><span className="notification-icon"><Icon size={18} /></span><div><div><h2>{item.title}</h2>{item.unread ? <i className="notice-dot" /> : null}</div><p>{item.description}</p><small>{item.type} · {item.time}</small></div><button className="icon-button" aria-label={'More options for ' + item.title}><MoreHorizontal size={18} /></button></article> })}</GlassCard></Page>
}

export function ProfilePage() {
  return <Page><PageIntro eyebrow="YOUR DIGILAW PROFILE" title="Profile" description="Manage the details shown in your legal intelligence workspace." /><div className="profile-layout"><GlassCard className="profile-card"><div className="profile-hero"><span className="avatar profile-avatar">AM</span><div><h2>Aarav Mehta</h2><p>demo@digilaw.app</p><Badge tone="purple">Case owner</Badge></div></div><div className="profile-stats"><span><strong>08</strong><small>Cases</small></span><span><strong>34</strong><small>Documents</small></span><span><strong>21</strong><small>Analyses</small></span></div></GlassCard><GlassCard className="profile-fields"><div className="panel-head"><div><SectionLabel icon={UserRound}>PERSONAL DETAILS</SectionLabel><h2>Profile information</h2></div><Button variant="secondary">Edit profile</Button></div><dl><div><dt>FULL NAME</dt><dd>Aarav Mehta</dd></div><div><dt>EMAIL ADDRESS</dt><dd>demo@digilaw.app</dd></div><div><dt>PHONE</dt><dd>+91 98765 43210</dd></div><div><dt>TIMEZONE</dt><dd>India Standard Time</dd></div></dl></GlassCard></div></Page>
}

export function SettingsPage() {
  const [theme, setTheme] = useState('Light')
  return <Page><PageIntro eyebrow="PREFERENCES" title="Settings" description="Control how your DigiLaw workspace looks and communicates." /><div className="settings-layout"><GlassCard className="settings-nav"><span className="settings-nav-active">Profile</span><span>Account</span><span>Appearance</span><span>Notifications</span><span>Privacy</span><span>Security</span></GlassCard><div className="settings-panels"><GlassCard><SectionLabel icon={UserRound}>PROFILE</SectionLabel><h2>Account details</h2><div className="settings-form"><label className="form-field"><span>Display name</span><input defaultValue="Aarav Mehta" /></label><label className="form-field"><span>Email address</span><input defaultValue="demo@digilaw.app" type="email" /></label><Button>Save changes</Button></div></GlassCard><GlassCard><SectionLabel icon={Settings2}>APPEARANCE</SectionLabel><h2>Choose your workspace theme</h2><div className="theme-options">{['Light', 'Dark', 'System'].map((option) => <button key={option} className={theme === option ? 'theme-active' : ''} onClick={() => setTheme(option)}><span className={'theme-preview preview-' + option.toLowerCase()} />{option}<i>{theme === option ? <Check size={16} /> : null}</i></button>)}</div><p className="settings-help">The luminous lavender light experience is the default DigiLaw theme.</p></GlassCard><GlassCard><SectionLabel icon={Bell}>NOTIFICATIONS</SectionLabel><h2>Keep important updates in view</h2><div className="toggle-list"><label><span><strong>Document processing</strong><small>When a document is ready for review</small></span><input type="checkbox" defaultChecked /></label><label><span><strong>Action plan reminders</strong><small>When an action item needs attention</small></span><input type="checkbox" defaultChecked /></label><label><span><strong>Product updates</strong><small>Occasional DigiLaw improvements</small></span><input type="checkbox" /></label></div></GlassCard></div></div></Page>
}

export function NotFound() {
  return <Page className="not-found-page"><GlassCard><span className="not-found-mark"><Scale size={38} /></span><SectionLabel>404 · CASE NOT FOUND</SectionLabel><h1>Looks like this page doesn&apos;t belong to this case.</h1><p>The workspace link may have changed, or the requested information is not available in this demo.</p><Link className="button button-primary" to="/dashboard">Return to dashboard <ArrowRight size={16} /></Link></GlassCard></Page>
}
