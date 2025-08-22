// frontend/src/pages/ProductDetail.jsx
import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    method: opts.method || 'GET',
    body: opts.body,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`)
  return data
}

// simple validators
const isDigits = (s, n) => typeof s === 'string' && /^\d+$/.test(s) && s.length === n
const isIntGte0 = (v) => Number.isInteger(v) && v >= 0

export default function ProductDetail() {
  const { id } = useParams()
  const { has } = useAuth()
  const canEdit = has('edit_stock')

  const [orig, setOrig] = useState(null)         // original product
  const [form, setForm] = useState(null)         // working copy
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  // load product
  useEffect(() => {
    (async () => {
      try {
        setErr(''); setMsg('')
        const data = await api(`/products/${id}`)
        setOrig(data)
        setForm({
          sku: data.sku ?? '',
          barcode: data.barcode ?? '',
          outer_barcode: data.outer_barcode ?? '',
          stock: data.stock ?? 0,
          low_stock_threshold: data.low_stock_threshold ?? 0,
          name: data.name ?? '',
        })
      } catch (e) {
        setErr(e.message)
      }
    })()
  }, [id])

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  // client-side validation state
  const validation = useMemo(() => {
    if (!form) return { ok: false, errors: {} }
    const errors = {}
    if (!isDigits(String(form.sku || ''), 8)) errors.sku = 'SKU must be exactly 8 digits'
    if ((form.barcode ?? '') !== '' && !isDigits(String(form.barcode), 13)) {
      errors.barcode = 'Barcode must be 13 digits or blank'
    }
    if ((form.outer_barcode ?? '') !== '' && !isDigits(String(form.outer_barcode), 13)) {
      errors.outer_barcode = 'Outer barcode must be 13 digits or blank'
    }
    const stock = Number(form.stock)
    const low = Number(form.low_stock_threshold)
    if (!isIntGte0(stock)) errors.stock = 'Stock must be an integer ≥ 0'
    if (!isIntGte0(low)) errors.low_stock_threshold = 'Low stock threshold must be an integer ≥ 0'
    return { ok: Object.keys(errors).length === 0, errors }
  }, [form])

  const dirty = useMemo(() => {
    if (!orig || !form) return false
    return (
      form.sku !== (orig.sku ?? '') ||
      (form.barcode || '') !== (orig.barcode || '') ||
      (form.outer_barcode || '') !== (orig.outer_barcode || '') ||
      Number(form.stock) !== Number(orig.stock) ||
      Number(form.low_stock_threshold) !== Number(orig.low_stock_threshold)
    )
  }, [orig, form])

  const save = async () => {
    if (!canEdit || !validation.ok || !dirty) return
    try {
      setBusy(true); setErr(''); setMsg('')
      const body = {
        sku: String(form.sku || ''),
        barcode: (form.barcode || '').trim(),              // server treats "" as null
        outer_barcode: (form.outer_barcode || '').trim(),  // server treats "" as null
        stock: Number(form.stock),
        low_stock_threshold: Number(form.low_stock_threshold),
      }
      const data = await api(`/products/${id}`, { method: 'PUT', body: JSON.stringify(body) })
      setOrig(data.product)
      // align form with server echo (normalise nulls as empty strings for inputs)
      setForm(f => ({
        ...f,
        sku: data.product.sku ?? '',
        barcode: data.product.barcode ?? '',
        outer_barcode: data.product.outer_barcode ?? '',
        stock: data.product.stock ?? 0,
        low_stock_threshold: data.product.low_stock_threshold ?? 0,
      }))
      setMsg(data.changed ? 'Saved' : 'No changes')
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  if (err) return <div className="text-red-600">{err}</div>
  if (!orig || !form) return <div>Loading…</div>

  return (
    <div className="max-w-xl mx-auto">
      <Link className="underline" to="/products">← Back to products</Link>
      <h2 className="text-xl font-semibold mt-2 mb-3">{orig.name}</h2>

      <div className="grid gap-3 bg-white border rounded-2xl p-4 shadow">
        <div className="grid gap-1">
          <label className="text-sm text-gray-600">SKU (EAN‑8)</label>
          <input
            className="border rounded px-3 py-2"
            value={form.sku}
            onChange={e => update('sku', e.target.value.trim())}
            disabled={!canEdit}
          />
          {validation.errors.sku && <div className="text-red-600 text-sm">{validation.errors.sku}</div>}
        </div>

        <div className="grid gap-1">
          <label className="text-sm text-gray-600">Barcode (EAN‑13)</label>
          <input
            className="border rounded px-3 py-2"
            value={form.barcode}
            onChange={e => update('barcode', e.target.value.trim())}
            placeholder="Leave blank to unset"
            disabled={!canEdit}
          />
          {validation.errors.barcode && <div className="text-red-600 text-sm">{validation.errors.barcode}</div>}
        </div>

        <div className="grid gap-1">
          <label className="text-sm text-gray-600">Outer barcode (EAN‑13)</label>
          <input
            className="border rounded px-3 py-2"
            value={form.outer_barcode}
            onChange={e => update('outer_barcode', e.target.value.trim())}
            placeholder="Leave blank to unset"
            disabled={!canEdit}
          />
          {validation.errors.outer_barcode && <div className="text-red-600 text-sm">{validation.errors.outer_barcode}</div>}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="grid gap-1">
            <label className="text-sm text-gray-600">Stock</label>
            <input
              className="border rounded px-3 py-2"
              value={form.stock}
              onChange={e => update('stock', e.target.value.replace(/[^\d-]/g, ''))}
              disabled={!canEdit}
            />
            {validation.errors.stock && <div className="text-red-600 text-sm">{validation.errors.stock}</div>}
          </div>

          <div className="grid gap-1">
            <label className="text-sm text-gray-600">Low stock threshold</label>
            <input
              className="border rounded px-3 py-2"
              value={form.low_stock_threshold}
              onChange={e => update('low_stock_threshold', e.target.value.replace(/[^\d-]/g, ''))}
              disabled={!canEdit}
            />
            {validation.errors.low_stock_threshold && <div className="text-red-600 text-sm">{validation.errors.low_stock_threshold}</div>}
          </div>
        </div>

        {canEdit ? (
          <button
            className="mt-1 px-4 py-2 rounded bg-black text-white disabled:opacity-50"
            onClick={save}
            disabled={!validation.ok || !dirty || busy}
            title={!validation.ok ? 'Fix validation errors' : (!dirty ? 'No changes to save' : '')}
          >
            {busy ? 'Saving…' : 'Save changes'}
          </button>
        ) : (
          <div className="text-sm text-gray-500">Read‑only (missing permission: edit_stock)</div>
        )}

        {msg && <div className="text-green-700">{msg}</div>}
        {err && <div className="text-red-600">{err}</div>}
      </div>
    </div>
  )
}
