import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

async function api(path) {
  const res = await fetch(`${API}${path}`, { credentials: 'include' })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
  return data
}

export default function Products() {
  const { user } = useAuth()
  const [q, setQ] = useState('')
  const [page, setPage] = useState(0)
  const [data, setData] = useState({ total: 0, items: [] })
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  const limit = 10
  useEffect(() => {
    (async () => {
      try {
        setLoading(true)
        const params = new URLSearchParams({
          q, limit: String(limit), offset: String(page * limit), sort: 'name', order: 'asc'
        })
        const out = await api(`/products/?${params}`)
        setData(out)
        setErr('')
      } catch (e) {
        setErr(e.message)
      } finally {
        setLoading(false)
      }
    })()
  }, [q, page])

  const maxPage = Math.max(0, Math.ceil(data.total / limit) - 1)

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-xl font-semibold mb-3">Products</h2>
      <div className="flex gap-2 mb-3">
        <input
          className="border rounded px-3 py-2 flex-1"
          placeholder="Search by name…"
          value={q}
          onChange={(e) => { setPage(0); setQ(e.target.value) }}
        />
      </div>
      {err && <div className="text-red-600 mb-2">{err}</div>}
      {loading ? (
        <div>Loading…</div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border rounded bg-white">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left p-2 border-b">SKU (EAN‑8)</th>
                  <th className="text-left p-2 border-b">Barcode (EAN‑13)</th>
                  <th className="text-left p-2 border-b">Name</th>
                  <th className="text-right p-2 border-b">Stock</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map(p => (
                  <tr key={p.product_id} className="border-b last:border-0">
                    <td className="p-2">{p.sku}</td>
                    <td className="p-2">{p.barcode}</td>
                    <td className="p-2">{p.name}</td>
                    <td className="p-2">
                        <a className="underline" href={`/products/${p.product_id}`}>{p.name}</a>
                    </td>
                    <td className="p-2 text-right">{p.stock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between mt-3">
            <div>{data.total} items</div>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1 border rounded disabled:opacity-50"
                onClick={() => setPage(p => Math.max(0, p-1))} disabled={page===0}>Prev</button>
              <span>Page {page+1} / {maxPage+1}</span>
              <button className="px-3 py-1 border rounded disabled:opacity-50"
                onClick={() => setPage(p => Math.min(maxPage, p+1))} disabled={page>=maxPage}>Next</button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
