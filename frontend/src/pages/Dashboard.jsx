import { useAuth } from '../context/AuthContext.jsx'
import { useNavigate } from 'react-router-dom'

const Dashboard = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  // Prevent rendering if user data isn't loaded yet
  if (!user || !user.permissions) {
    return <p>Loading user data...</p>
  }

  return (
    <div>
      <h1>Welcome, {user.username}</h1>
      <p>Your permissions: {user.permissions.join(', ')}</p>

      {user.permissions.includes('manage_users') && (
        <button onClick={() => alert('Redirect to Admin Panel')}>Admin Panel</button>
      )}

      {user.permissions.includes('make_orders') && (
        <button onClick={() => alert('Redirect to Store Ordering')}>Place Order</button>
      )}

      {user.permissions.includes('edit_stock') && (
        <button onClick={() => alert('Redirect to Stock Editor')}>Edit Stock</button>
      )}

      <button onClick={handleLogout} style={{ marginTop: '20px' }}>
        Logout
      </button>
    </div>
  )
}

export default Dashboard
