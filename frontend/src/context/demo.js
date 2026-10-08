import { createContext, useContext } from 'react'

export const DemoContext = createContext(null)

export function useDemoData() {
  const context = useContext(DemoContext)
  if (!context) throw new Error('useDemoData must be used inside DemoProvider')
  return context
}
