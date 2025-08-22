from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from ..models import Product
from ..permissions import require_permission
from .. import db

bp = Blueprint('products', __name__)

def to_dict(p: Product):
    return {
        "product_id": p.product_id,
        "name": p.name,
        "sku": p.sku,                     # 8 digits
        "barcode": p.barcode,             # 13 digits or null
        "outer_barcode": p.outer_barcode, # 13 digits or null
        "stock": p.stock,
        "low_stock_threshold": p.low_stock_threshold,
    }

@bp.route('/', methods=['GET'])
@require_permission('view_products')
def list_products():
    q = (request.args.get('q') or "").strip()
    limit = max(1, min(int(request.args.get('limit', 20)), 100))
    offset = max(0, int(request.args.get('offset', 0)))

    query = Product.query

    if q:
        if q.isdigit():
            # digits: try SKU (8d) + barcodes (13d), allow prefix matches
            conds = []
            if len(q) <= 8:
                conds += [Product.sku == q, Product.sku.like(f"{q}%")]
            if len(q) <= 13:
                conds += [
                    Product.barcode == q, Product.barcode.like(f"{q}%"),
                    Product.outer_barcode == q, Product.outer_barcode.like(f"{q}%"),
                ]
            # always include name fallback
            conds.append(Product.name.ilike(f"%{q}%"))
            query = query.filter(or_(*conds))
        else:
            query = query.filter(Product.name.ilike(f"%{q}%"))

    # stable sorting
    sort = (request.args.get('sort') or 'name').lower()
    order = (request.args.get('order') or 'asc').lower()
    col = Product.name if sort == 'name' else Product.product_id
    query = query.order_by(col.asc() if order != 'desc' else col.desc())

    total = query.count()
    items = query.limit(limit).offset(offset).all()

    return jsonify({"total": total, "items": [to_dict(p) for p in items]})

@bp.route('/<int:pid>', methods=['GET'])
@require_permission('view_products')
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify(to_dict(p))

@bp.route('/<int:pid>', methods=['PUT'])
@require_permission('edit_stock')
def update_product(pid):
    """
    Updates limited product fields. Guarded by 'edit_stock'.
    Accepts JSON with any of: stock, low_stock_threshold, sku, barcode, outer_barcode.
    Rules:
      - sku: exactly 8 digits
      - barcode/outer_barcode: 13 digits or null/empty
      - stock, low_stock_threshold: integers ≥ 0
    Returns: { ok: true, product: {...}, changed: bool }
    """
    p = Product.query.get_or_404(pid)
    data = request.get_json(silent=True) or {}

    # helpers
    def is_digits(s, n):
        return isinstance(s, str) and s.isdigit() and len(s) == n

    # Current values are defaults if not provided
    next_stock = data.get('stock', p.stock)
    next_low   = data.get('low_stock_threshold', p.low_stock_threshold)
    next_sku   = data.get('sku', p.sku)
    next_bar   = data.get('barcode', p.barcode)
    next_outer = data.get('outer_barcode', p.outer_barcode)

    # Normalise empty strings for barcodes to None
    if isinstance(next_bar, str) and next_bar.strip() == "":
        next_bar = None
    if isinstance(next_outer, str) and next_outer.strip() == "":
        next_outer = None

    # Validate identifiers
    if not is_digits(next_sku, 8):
        return jsonify({'error': 'sku must be exactly 8 digits'}), 400
    if next_bar is not None and not is_digits(str(next_bar), 13):
        return jsonify({'error': 'barcode must be 13 digits or null'}), 400
    if next_outer is not None and not is_digits(str(next_outer), 13):
        return jsonify({'error': 'outer_barcode must be 13 digits or null'}), 400

    # Validate numerics
    try:
        next_stock = int(next_stock)
        next_low   = int(next_low)
        if next_stock < 0 or next_low < 0:
            raise ValueError("negative")
    except Exception:
        return jsonify({'error': 'stock and low_stock_threshold must be integers ≥ 0'}), 400

    # No-op detection
    if (next_stock == p.stock and next_low == p.low_stock_threshold and
        next_sku == p.sku and next_bar == p.barcode and next_outer == p.outer_barcode):
        return jsonify({'ok': True, 'product': to_dict(p), 'changed': False})

    # Apply & persist
    p.stock = next_stock
    p.low_stock_threshold = next_low
    p.sku = next_sku
    p.barcode = next_bar
    p.outer_barcode = next_outer

    db.session.commit()
    return jsonify({'ok': True, 'product': to_dict(p), 'changed': True})
