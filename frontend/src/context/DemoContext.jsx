import { useState } from 'react'
import { cases as initialCases } from '../data/mockData'
import { DemoContext } from './demo'

export function DemoProvider({ children }) {
  const [allCases, setAllCases] = useState(initialCases)

  function createCase(values) {
    const nextCase = {
      id: 'DL-2026-' + String(30 + allCases.length).padStart(3, '0'),
      title: values.title,
      category: values.type,
      status: 'Analysis in Progress',
      tone: 'info',
      jurisdiction: values.jurisdiction || 'Not specified',
      createdAt: 'Today',
      updatedAt: 'Just now',
      progress: 8,
      evidence: 0,
      documents: 0,
      nextAction: 'Add documents or evidence',
      description: values.description,
    }
    setAllCases((current) => [nextCase, ...current])
    return nextCase
  }

  return <DemoContext.Provider value={{ cases: allCases, createCase }}>{children}</DemoContext.Provider>
}
