import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useEffect } from 'react'

export default function Login() {
const { login, user } = useAuth()
const [username, setUsername] = useState('')
const [password, setPassword] = useState('')
const [error, setError] = useState('')
const [busy, setBusy] = useState(false)
const navigate = useNavigate()

useEffect(() => {
    if (user?.authenticated) navigate('/', { replace: true });
  }, [user?.authenticated, navigate]);


const handleSubmit = async (e) => {
e.preventDefault()
setBusy(true)
setError('')
try {
await login(username, password)
navigate('/')
} catch (err) {
setError(err.message || 'Login failed')
} finally {
setBusy(false)
}
}


return (
<div className="max-w-sm mx-auto mt-16 p-6 bg-white border rounded-2xl shadow">
<h1 className="text-xl font-semibold mb-4">Sign in</h1>
<form onSubmit={handleSubmit} className="grid gap-3">
<input
className="border rounded px-3 py-2"
placeholder="Username"
autoComplete="username"
value={username}
onChange={(e) => setUsername(e.target.value)}
/>
<input
className="border rounded px-3 py-2"
placeholder="Password"
type="password"
autoComplete="current-password"
value={password}
onChange={(e) => setPassword(e.target.value)}
/>
{error && <div className="text-red-600 text-sm">{error}</div>}
<button
className="px-4 py-2 rounded bg-black text-white disabled:opacity-50"
disabled={busy}
type="submit"
>
{busy ? 'Signing in…' : 'Sign in'}
</button>
</form>
<p className="text-xs text-gray-500 mt-3">Try root / rootpass (seed).</p>
</div>
)
}