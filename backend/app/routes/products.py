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
    p = Product.query.get_or_404(pid)
    data = request.get_json(silent=True) or {}

    def is_digits(s, n): return isinstance(s, str) and s.isdigit() and len(s) == n

    stock = data.get('stock', p.stock)
    low = data.get('low_stock_threshold', p.low_stock_threshold)
    sku = data.get('sku', p.sku)
    barcode = data.get('barcode', p.barcode)
    outer = data.get('outer_barcode', p.outer_barcode)

    if not is_digits(sku, 8):
        return jsonify({'error': 'sku must be 8 digits'}), 400
    if barcode not in (None, "") and not is_digits(str(barcode), 13):
        return jsonify({'error': 'barcode must be 13 digits or null'}), 400
    if outer not in (None, "") and not is_digits(str(outer), 13):
        return jsonify({'error': 'outer_barcode must be 13 digits or null'}), 400
    try:
        stock = int(stock); low = int(low)
        if stock < 0 or low < 0:
            raise ValueError()
    except Exception:
        return jsonify({'error': 'stock and low_stock_threshold must be integers ≥ 0'}), 400

    p.stock = stock
    p.low_stock_threshold = low
    p.sku = sku
    p.barcode = barcode or None
    p.outer_barcode = outer or None

    db.session.commit()
    return jsonify({'ok': True, 'product': to_dict(p)})
