import { Routes, Route, Navigate, Link } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import AdminUsers from './pages/AdminUsers.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import { useAuth } from './context/AuthContext.jsx'
import Products from './pages/Products.jsx'


export default function App() {
const { user, logout } = useAuth()
return (
<div className="min-h-screen bg-gray-50 text-gray-900">
<header className="flex items-center justify-between px-4 py-3 border-b bg-white">
<div className="font-semibold">WarehouseOne</div>
<nav className="flex items-center gap-3">
{user?.authenticated ? (
<>
<Link className="underline" to="/">Dashboard</Link>
<button onClick={logout} className="px-3 py-1 border rounded">Logout</button>
</>
) : (
<Link className="underline" to="/login">Login</Link>
)}
</nav>
</header>
<main className="p-4">
<Routes>
<Route path="/login" element={<Login />} />
<Route
path="/"
element={
<ProtectedRoute>
<Dashboard />
</ProtectedRoute>
}
/>
<Route
path="/admin/users"
element={
<ProtectedRoute requiredPermission="grant_permissions">
<AdminUsers />
</ProtectedRoute>
}
/>
<Route
  path="/products"
  element={
    <ProtectedRoute requiredPermission="view_products">
      <Products />
    </ProtectedRoute>
  }
/>
<Route path="*" element={<Navigate to="/" />} />
</Routes>
</main>
<footer className="px-4 py-3 text-sm text-gray-500">v0.2.0 • Dev</footer>
</div>
)
}