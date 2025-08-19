import { useEffect, useState } from 'react'


const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'


async function api(path, opts = {}) {
const res = await fetch(`${API_BASE}${path}`, { credentials: 'include', ...opts })
const data = await res.json().catch(() => ({}))
if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
return data
}


export default function AdminUsers() {
const [users, setUsers] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState('')


useEffect(() => {
(async () => {
try {
const data = await api('/admin/users')
setUsers(data)
} catch (e) {
setError(e.message)
} finally {
setLoading(false)
}
})()
}, [])


if (loading) return <div>Loading…</div>
if (error) return <div className="text-red-600">{error}</div>


return (
<div className="max-w-2xl mx-auto">
<h2 className="text-xl font-semibold mb-3">Users</h2>
<div className="overflow-x-auto">
<table className="min-w-full text-sm border rounded-lg bg-white">
<thead className="bg-gray-100">
<tr>
<th className="text-left p-2 border-b">ID</th>
<th className="text-left p-2 border-b">Username</th>
</tr>
</thead>
<tbody>
{users.map((u) => (
<tr key={u.user_id} className="border-b last:border-0">
<td className="p-2">{u.user_id}</td>
<td className="p-2">{u.username}</td>
</tr>
))}
</tbody>
</table>
</div>
</div>
)
}