from flask import Blueprint, jsonify, request
from ..models import Product
# Import the require_permission decorator to enforce access control on this route.
from ..permissions import require_permission

bp = Blueprint('products', __name__)

@bp.route('/', methods=['GET'])
@require_permission('view_products')
def list_products():
    q = (request.args.get('q') or "").strip()
    limit = min(int(request.args.get('limit', 20)), 100)
    offset = int(request.args.get('offset', 0))

    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(Product.name.ilike(like))

    # NEW: sorting
    sort = (request.args.get('sort') or 'name').lower()
    order = (request.args.get('order') or 'asc').lower()
    col = Product.name if sort == 'name' else Product.product_id
    query = query.order_by(col.asc() if order != 'desc' else col.desc())

    total = query.count()
    items = query.limit(limit).offset(offset).all()

    def to_dict(p: Product):
        return {
            "product_id": p.product_id,
            "name": p.name,
            "sku": p.sku,
            "barcode": p.barcode,
            "outer_barcode": p.outer_barcode,
            "brand": p.brand,
            "price": str(p.price),
            "stock": p.stock,
            "low_stock_threshold": p.low_stock_threshold,
        }

    return jsonify({"total": total, "items": [to_dict(p) for p in items]})

@bp.route('/<int:pid>', methods=['GET'])
@require_permission('view_products')
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify(p.to_dict())

@bp.route('/<int:pid>', methods=['PUT'])
@require_permission('edit_stock')
def update_product(pid):
    p = Product.query.get_or_404(pid)
    data = request.get_json(silent=True) or {}
    # validate
    def is_digits(s, n): return isinstance(s, str) and s.isdigit() and len(s) == n
    stock = data.get('stock', p.stock)
    low = data.get('low_stock_threshold', p.low_stock_threshold)
    sku = data.get('sku', p.sku)
    barcode = data.get('barcode', p.barcode)
    outer = data.get('outer_barcode', p.outer_barcode)

    if not is_digits(sku, 8): return jsonify({'error':'sku must be 8 digits'}), 400
    if barcode is not None and barcode != '' and not is_digits(str(barcode), 13):
        return jsonify({'error':'barcode must be 13 digits or null'}), 400
    if outer is not None and outer != '' and not is_digits(str(outer), 13):
        return jsonify({'error':'outer_barcode must be 13 digits or null'}), 400
    try:
        stock = int(stock); low = int(low)
        if stock < 0 or low < 0: raise ValueError()
    except Exception:
        return jsonify({'error':'stock and low_stock_threshold must be integers ≥ 0'}), 400

    # apply
    p.stock = stock
    p.low_stock_threshold = low
    p.sku = sku
    p.barcode = barcode or None
    p.outer_barcode = outer or None

    db.session.commit()
    return jsonify({'ok': True, 'product': p.to_dict()})
