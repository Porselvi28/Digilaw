import { useMemo, useState } from 'react'
import { demoUser } from '../data/mockData'
import { AuthContext } from './auth'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const value = useMemo(() => ({
    user,
    login(email, password) {
      if (email.toLowerCase() === 'demo@digilaw.app' && password === 'Demo123!') {
        setUser(demoUser)
        return { success: true }
      }
      return { success: false, message: 'Use the demo account: demo@digilaw.app / Demo123!' }
    },
    register(name, email) {
      setUser({ ...demoUser, name, email, initials: name.split(' ').map((word) => word[0]).join('').slice(0, 2).toUpperCase() })
    },
    logout() {
      setUser(null)
    },
  }), [user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
