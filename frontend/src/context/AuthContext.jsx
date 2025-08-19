import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'

const AuthContext = createContext(null)
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

async function api(path, { method = 'GET', body, headers } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...(headers || {}) },
    body: body ? JSON.stringify(body) : undefined,
    credentials: 'include', // send/receive cookie
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const message = data?.error || `HTTP ${res.status}`
    throw new Error(message)
  }
  return data
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null) // { authenticated, username, permissions[] }
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const normalise = (data) => {
  const authenticated =
    typeof data?.authenticated !== 'undefined'
      ? !!data.authenticated
      : (data?.user != null) || (data?.user_id != null);

  const username =
    data?.username ?? data?.user?.username ?? null;

  const permissions = Array.isArray(data?.permissions) ? data.permissions : [];

  return { authenticated, username, permissions };
};

  const refresh = useCallback(async () => {
    try {
      setLoading(true)
      const data = await api('/auth/me')
      setUser(normalise(data))
      setError(null)
    } catch {
      setUser({ authenticated: false, username: null, permissions: [] })
      setError(null) // quiet on cold start
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const login = async (username, password) => {
    await api('/auth/login', { method: 'POST', body: { username, password } })
    // Optimistic flip so navigation to "/" isn't bounced by ProtectedRoute
    setUser((u) => ({ ...(u || {}), authenticated: true }))
    await refresh() // confirm & populate username/permissions
  }

  const logout = async () => {
    try {
      await api('/auth/logout', { method: 'POST' })
    } catch {
      // ignore
    }
    setUser({ authenticated: false, username: null, permissions: [] })
  }

  const has = (perm) =>
    user?.permissions?.includes('*') || user?.permissions?.includes(perm)

  const value = { user, loading, error, login, logout, has, refresh }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
