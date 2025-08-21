import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

async function api(path, opts={}) {
  const res = await fetch(`${API}${path}`, { credentials:'include', headers:{'Content-Type':'application/json'}, ...opts })
  const data = await res.json().catch(()=>({}))
  if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
  return data
}

export default function ProductDetail() {
  const { id } = useParams()
  const { has } = useAuth()
  const canEdit = has('edit_stock')
  const [p, setP] = useState(null)
  const [stock, setStock] = useState('')
  const [low, setLow] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const data = await api(`/products/${id}`)
        setP(data); setStock(String(data.stock)); setLow(String(data.low_stock_threshold ?? 10))
      } catch (e) { setErr(e.message) }
    })()
  }, [id])

  const save = async () => {
    try {
      setErr(''); setMsg('')
      const body = { stock: Number(stock), low_stock_threshold: Number(low) }
      const data = await api(`/products/${id}`, { method:'PUT', body: JSON.stringify(body) })
      setP(data.product); setMsg('Saved')
    } catch (e) { setErr(e.message) }
  }

  if (err) return <div className="text-red-600">{err}</div>
  if (!p) return <div>Loading…</div>

  return (
    <div className="max-w-xl mx-auto">
      <Link className="underline" to="/products">← Back to products</Link>
      <h2 className="text-xl font-semibold mt-2 mb-3">{p.name}</h2>
      <div className="grid gap-2 bg-white border rounded p-4">
        <div><b>SKU:</b> {p.sku}</div>
        <div><b>Barcode:</b> {p.barcode || '—'}</div>
        <div><b>Outer barcode:</b> {p.outer_barcode || '—'}</div>
        <div className="grid grid-cols-2 gap-3 mt-2">
          <label className="block">
            <span className="text-sm text-gray-600">Stock</span>
            <input className="border rounded px-3 py-2 w-full" value={stock} onChange={e=>setStock(e.target.value)} disabled={!canEdit}/>
          </label>
          <label className="block">
            <span className="text-sm text-gray-600">Low stock threshold</span>
            <input className="border rounded px-3 py-2 w-full" value={low} onChange={e=>setLow(e.target.value)} disabled={!canEdit}/>
          </label>
        </div>
        {canEdit ? (
          <button className="mt-2 px-4 py-2 border rounded" onClick={save}>Save</button>
        ) : (
          <div className="text-sm text-gray-500 mt-1">Read‑only (missing permission: edit_stock)</div>
        )}
        {msg && <div className="text-green-700">{msg}</div>}
        {err && <div className="text-red-600">{err}</div>}
      </div>
    </div>
  )
}
