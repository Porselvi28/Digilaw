export const demoUser = {
  name: 'Aarav Mehta',
  email: 'demo@digilaw.app',
  initials: 'AM',
  role: 'Case owner',
}

export const cases = [
  {
    id: 'DL-2026-014',
    title: 'Property Dispute',
    category: 'Property',
    status: 'Analysis Ready',
    tone: 'success',
    jurisdiction: 'Bengaluru, Karnataka',
    createdAt: '12 Aug 2026',
    updatedAt: 'Today, 10:24 AM',
    progress: 78,
    evidence: 12,
    documents: 8,
    nextAction: 'Review ownership-chain findings',
    description: 'A title and possession dispute concerning a residential property and related ownership documents.',
  },
  {
    id: 'DL-2026-018',
    title: 'College Ragging Complaint',
    category: 'Education / Ragging',
    status: 'Action Required',
    tone: 'danger',
    jurisdiction: 'Pune, Maharashtra',
    createdAt: '29 Aug 2026',
    updatedAt: 'Yesterday',
    progress: 56,
    evidence: 7,
    documents: 5,
    nextAction: 'Add witness statement details',
    description: 'A structured record of a campus complaint, supporting messages, and reported incidents.',
  },
  {
    id: 'DL-2026-021',
    title: 'Consumer Complaint',
    category: 'Consumer',
    status: 'Documents Missing',
    tone: 'warning',
    jurisdiction: 'New Delhi',
    createdAt: '01 Sep 2026',
    updatedAt: '2 days ago',
    progress: 42,
    evidence: 4,
    documents: 3,
    nextAction: 'Upload invoice and service correspondence',
    description: 'A complaint concerning a defective product, warranty coverage, and an unresolved service request.',
  },
  {
    id: 'DL-2026-025',
    title: 'Employment Dispute',
    category: 'Employment',
    status: 'Analysis in Progress',
    tone: 'info',
    jurisdiction: 'Mumbai, Maharashtra',
    createdAt: '05 Sep 2026',
    updatedAt: 'Processing now',
    progress: 64,
    evidence: 9,
    documents: 6,
    nextAction: 'Await document classification',
    description: 'A workplace dispute workspace with employment terms, communication records, and a chronology of events.',
  },
]

export const documents = [
  { id: 'doc-01', caseId: 'DL-2026-014', name: 'Property_Deed.pdf', kind: 'Ownership Document', size: '2.4 MB', uploaded: 'Today, 9:14 AM', status: 'Analyzed', tone: 'success' },
  { id: 'doc-02', caseId: 'DL-2026-014', name: 'Tax_Receipts_2022-25.pdf', kind: 'Financial Record', size: '1.8 MB', uploaded: 'Yesterday', status: 'Analyzed', tone: 'success' },
  { id: 'doc-03', caseId: 'DL-2026-014', name: 'Notice_Reply.docx', kind: 'Correspondence', size: '476 KB', uploaded: '08 Sep 2026', status: 'Needs Review', tone: 'warning' },
  { id: 'doc-04', caseId: 'DL-2026-018', name: 'Complaint_Draft.pdf', kind: 'Complaint', size: '946 KB', uploaded: '08 Sep 2026', status: 'Processing', tone: 'info' },
  { id: 'doc-05', caseId: 'DL-2026-018', name: 'Evidence_Photo_03.jpg', kind: 'Evidence Image', size: '4.1 MB', uploaded: '07 Sep 2026', status: 'Analyzed', tone: 'success' },
  { id: 'doc-06', caseId: 'DL-2026-021', name: 'Purchase_Receipt.pdf', kind: 'Invoice', size: '580 KB', uploaded: '06 Sep 2026', status: 'Uploaded', tone: 'neutral' },
  { id: 'doc-07', caseId: 'DL-2026-025', name: 'Employment_Contract.pdf', kind: 'Employment Record', size: '1.2 MB', uploaded: '05 Sep 2026', status: 'Analyzed', tone: 'success' },
]

export const evidenceItems = [
  { id: 'EV-014-01', caseId: 'DL-2026-014', type: 'Document', title: 'Registered property deed', source: 'Property_Deed.pdf', date: '14 Mar 2018', status: 'Verified', tone: 'success', relevance: 'High relevance', description: 'Recorded ownership information and transfer details extracted for review.' },
  { id: 'EV-014-02', caseId: 'DL-2026-014', type: 'Correspondence', title: 'Notice response', source: 'Notice_Reply.docx', date: '02 Sep 2026', status: 'Needs review', tone: 'warning', relevance: 'Medium relevance', description: 'A written response that may clarify the current position of the parties.' },
  { id: 'EV-014-03', caseId: 'DL-2026-014', type: 'Financial record', title: 'Property tax receipts', source: 'Tax_Receipts_2022-25.pdf', date: '2022–2025', status: 'Verified', tone: 'success', relevance: 'High relevance', description: 'Receipt sequence identified as potentially useful supporting material.' },
  { id: 'EV-018-01', caseId: 'DL-2026-018', type: 'Image', title: 'Campus incident image', source: 'Evidence_Photo_03.jpg', date: '31 Aug 2026', status: 'Unclassified', tone: 'neutral', relevance: 'For review', description: 'Image metadata and visible details await human verification.' },
]

export const legalReferences = [
  { id: 'ref-1', title: 'Transfer of Property Act, 1882', section: 'Section 54', type: 'STATUTORY REFERENCE', relevance: 'HIGH RELEVANCE', tone: 'success', summary: 'Example reference for reviewing how a sale of immovable property is described in the available materials.' },
  { id: 'ref-2', title: 'Registration Act, 1908', section: 'Section 17', type: 'STATUTORY REFERENCE', relevance: 'MEDIUM RELEVANCE', tone: 'info', summary: 'Example reference to verify registration requirements against the documents in this workspace.' },
  { id: 'ref-3', title: 'Evidence Act reference', section: 'Documentary material', type: 'REFERENCE FOR REVIEW', relevance: 'REFERENCE', tone: 'neutral', summary: 'A neutral prompt to review the provenance and completeness of documentary material.' },
]

export const analysisStages = [
  { title: 'Document uploaded', detail: 'Source materials safely added to the case workspace.', state: 'complete' },
  { title: 'OCR / text extraction', detail: 'Text and document structure prepared for review.', state: 'complete' },
  { title: 'Information extraction', detail: 'People, dates, events, and records organized.', state: 'complete' },
  { title: 'Evidence classification', detail: 'Evidence is being grouped by source and relevance.', state: 'active' },
  { title: 'Legal relevance', detail: 'Potential references are queued for contextual review.', state: 'upcoming' },
  { title: 'Reference matching', detail: 'Related legal material will be surfaced here.', state: 'upcoming' },
  { title: 'Analysis summary', detail: 'A structured review summary will be available next.', state: 'upcoming' },
]

export const similarCases = [
  { id: 'SC-4218', title: 'Ownership documentation dispute', similarity: 91, type: 'Property', issue: 'Document chain and possession records', metadata: 'Example reference · District court material', note: 'Shares a document-led pattern. Review source material and procedural context with a qualified professional.' },
  { id: 'SC-3874', title: 'Registered sale deed review', similarity: 84, type: 'Property', issue: 'Registration and transfer documentation', metadata: 'Example reference · High court material', note: 'May be a useful point of comparison for document review; it is not a prediction or legal conclusion.' },
  { id: 'SC-2941', title: 'Possession and title correspondence', similarity: 78, type: 'Property', issue: 'Written notices and supporting records', metadata: 'Example reference · Civil matter', note: 'Surfaces comparable themes in the indexed material for review.' },
]

export const actionPlan = [
  { order: '01', title: 'Collect missing documents', status: 'Completed', tone: 'success', priority: 'High', documents: 'Property deed, tax receipts', description: 'The currently available record includes the core ownership materials.' },
  { order: '02', title: 'Review extracted information', status: 'In Progress', tone: 'info', priority: 'High', documents: 'Notice reply', description: 'Confirm names, dates, and factual statements extracted from correspondence.' },
  { order: '03', title: 'Verify relevant legal references', status: 'Upcoming', tone: 'neutral', priority: 'Medium', documents: 'Reference notes', description: 'Review each surfaced reference against the actual facts and jurisdiction.' },
  { order: '04', title: 'Prepare required documentation', status: 'Upcoming', tone: 'neutral', priority: 'Medium', documents: 'Chronology, verified copies', description: 'Organize reviewed material into a clear evidence and document set.' },
  { order: '05', title: 'Seek appropriate guidance', status: 'Needs Attention', tone: 'warning', priority: 'High', documents: 'Complete case bundle', description: 'Important decisions should be verified with a qualified legal professional.' },
]

export const notifications = [
  { id: 1, title: 'Property_Deed.pdf processed', description: 'Text extraction and document classification are complete.', time: '14 minutes ago', type: 'Document processed', icon: 'file', unread: true },
  { id: 2, title: 'Case analysis is ready for review', description: 'New AI-assisted evidence findings are available in Property Dispute.', time: '2 hours ago', type: 'Analysis completed', icon: 'sparkles', unread: true },
  { id: 3, title: 'A document may be missing', description: 'Consider adding the prior ownership transfer record for review.', time: 'Yesterday', type: 'Missing document detected', icon: 'alert', unread: false },
  { id: 4, title: 'Action required for College Ragging Complaint', description: 'A witness statement detail needs clarification.', time: '2 days ago', type: 'Action required', icon: 'checklist', unread: false },
]

export const initialConversation = [
  { id: 1, role: 'assistant', text: 'I can help you explore the information in your DigiLaw workspace. What would you like to review?', time: '10:22 AM' },
  { id: 2, role: 'user', text: 'What documents are missing from my case?', time: '10:23 AM' },
  { id: 3, role: 'assistant', text: 'For the Property Dispute demo workspace, consider verifying whether the prior ownership transfer record and a complete correspondence chronology are available. This is an AI-assisted organizational prompt, not legal advice.', time: '10:23 AM', sources: ['Case workspace', 'Document completeness review'] },
]

export const dashboardMetrics = [
  { label: 'Active Cases', value: '08', detail: 'Across 4 categories', icon: 'briefcase', tone: 'purple' },
  { label: 'Documents', value: '34', detail: '6 added this week', icon: 'file', tone: 'blue' },
  { label: 'Evidence Analyzed', value: '21', detail: '3 ready for review', icon: 'shield', tone: 'green' },
  { label: 'Pending Actions', value: '05', detail: '2 need attention', icon: 'checklist', tone: 'gold' },
]
