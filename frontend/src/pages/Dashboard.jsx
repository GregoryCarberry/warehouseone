import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'


export default function Dashboard() {
const { user, has, refresh } = useAuth()


return (
<div className="max-w-3xl mx-auto">
<div className="mb-4">
<h2 className="text-2xl font-semibold">Welcome, {user?.username || 'User'}</h2>
<p className="text-gray-600">Permissions: {user?.permissions?.join(', ') || '(none)'}
<button className="ml-3 underline" onClick={refresh}>refresh</button>
</p>
</div>


<div className="grid sm:grid-cols-2 gap-4">
<section className="p-4 border rounded-xl bg-white">
<h3 className="font-semibold mb-2">Quick actions</h3>
<ul className="list-disc pl-5">
{has('grant_permissions') && (
<li><Link className="underline" to="/admin/users">Admin → Users</Link></li>
)}
<li><a className="underline" href="#" onClick={(e) => e.preventDefault()}>Products (coming soon)</a></li>
</ul>
</section>
</div>
</div>
)
}