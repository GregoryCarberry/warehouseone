from flask import Blueprint, jsonify, request
from ..models import Product

bp = Blueprint('products', __name__)

@bp.route('/', methods=['GET'])
def list_products():
    q = (request.args.get('q') or "").strip()
    limit = min(int(request.args.get('limit', 20)), 100)
    offset = int(request.args.get('offset', 0))

    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(Product.name.ilike(like))

    total = query.count()
    items = query.order_by(Product.product_id).limit(limit).offset(offset).all()

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
