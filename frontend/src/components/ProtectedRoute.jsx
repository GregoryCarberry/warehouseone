import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function ProtectedRoute({ children, requiredPermission }) {
  const { user, loading, has } = useAuth();
  if (loading) return <div>Loading…</div>;
  if (!user?.authenticated) return <Navigate to="/login" replace />;
  if (requiredPermission && !has(requiredPermission))
    return <div>Forbidden (missing permission: {requiredPermission})</div>;
  return children;
}