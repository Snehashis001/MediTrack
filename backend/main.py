import os
import uuid
from contextlib import asynccontextmanager

try:
    from database import get_db, init_db
except ImportError:
    from backend.database import get_db, init_db

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="MediTrack API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CartItemPayload(BaseModel):
    product_id: int
    quantity: int = 1


class OrderPayload(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: str
    prescription_id: int | None = None


def compute_cart(conn):
    q = """SELECT c.id, c.product_id, c.quantity, p.name, p.generic_name,
                  p.category, p.price, p.mrp, p.dosage, p.requires_prescription, p.image_url
           FROM cart_items c JOIN products p ON c.product_id = p.id ORDER BY c.added_at DESC"""
    items = [dict(r) for r in conn.execute(q).fetchall()]
    sub = round(sum(i["price"] * i["quantity"] for i in items), 2)
    mrp = round(sum(i["mrp"] * i["quantity"] for i in items), 2)
    disc = round(mrp - sub, 2) if mrp > sub else 0.0
    fee = 0.0 if (sub >= 35.0 or not items) else 4.99
    return {
        "items": items,
        "items_count": sum(i["quantity"] for i in items),
        "subtotal": sub,
        "mrp_total": mrp,
        "discount": disc,
        "delivery_fee": fee,
        "total": round(sub + fee, 2),
        "has_rx_items": any(i["requires_prescription"] == 1 for i in items),
        "free_shipping_threshold": 35.0,
    }


@app.get("/api/categories")
def get_categories():
    with get_db() as conn:
        q = "SELECT category, COUNT(*) as count FROM products GROUP BY category"
        return [dict(r) for r in conn.execute(q)]


@app.get("/api/products")
def get_products(
    category: str | None = None, search: str | None = None, sort: str | None = "default"
):
    q, params = "SELECT * FROM products WHERE in_stock = 1", []
    if category and category.lower() != "all":
        q += " AND category = ?"
        params.append(category)
    if search:
        q += " AND (name LIKE ? OR generic_name LIKE ? OR description LIKE ?)"
        t = f"%{search.strip()}%"
        params.extend([t, t, t])
    sort_orders = {
        "price_asc": "price ASC",
        "price_desc": "price DESC",
        "rating": "rating DESC",
        "name": "name ASC",
    }
    q += f" ORDER BY {sort_orders.get(sort, 'is_bestseller DESC, id ASC')}"
    with get_db() as conn:
        return [dict(r) for r in conn.execute(q, params)]


@app.get("/api/cart")
def read_cart():
    with get_db() as conn:
        return compute_cart(conn)


@app.post("/api/cart")
def update_cart(item: CartItemPayload):
    if item.quantity < 1:
        return remove_cart(item.product_id)
    with get_db() as conn:
        if not conn.execute(
            "SELECT id FROM products WHERE id = ?", (item.product_id,)
        ).fetchone():
            raise HTTPException(status_code=404, detail="Product not found")
        q = """INSERT INTO cart_items (product_id, quantity) VALUES (?, ?)
               ON CONFLICT(product_id) DO UPDATE SET quantity = excluded.quantity"""
        conn.execute(q, (item.product_id, item.quantity))
        conn.commit()
        return compute_cart(conn)


@app.delete("/api/cart/{product_id}")
@app.delete("/api/cart")
def remove_cart(product_id: int | None = None):
    with get_db() as conn:
        sql = "DELETE FROM cart_items" + (" WHERE product_id = ?" if product_id else "")
        conn.execute(sql, (product_id,) if product_id else ())
        conn.commit()
        return compute_cart(conn)


@app.post("/api/prescriptions/upload")
def upload_prescription(
    file: UploadFile = File(...),  # noqa: B008
    patient_name: str | None = Form(None),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=400, detail="Only PDF, JPG, PNG are supported.")
    data = file.file.read()
    if not (1 <= len(data) <= 5 * 1024 * 1024):
        raise HTTPException(
            status_code=400, detail="File must be between 1 byte and 5MB."
        )
    path = os.path.join(UPLOAD_DIR, f"rx_{uuid.uuid4().hex[:8]}_{file.filename}")
    with open(path, "wb") as f:
        f.write(data)
    with get_db() as conn:
        cur = conn.cursor()
        q = "INSERT INTO prescriptions (filename, filepath, file_size, content_type, patient_name) VALUES (?,?,?,?,?)"
        mime = file.content_type or "image/jpeg"
        cur.execute(q, [file.filename, path, len(data), mime, patient_name or "Self"])
        conn.commit()
        return {
            "success": True,
            "prescription_id": cur.lastrowid,
            "filename": file.filename,
            "size_kb": round(len(data) / 1024, 1),
            "status": "Verified for Order",
            "message": "Prescription validated and attached to your session successfully.",
        }


@app.post("/api/orders")
def create_order(p: OrderPayload):
    with get_db() as conn:
        c = compute_cart(conn)
        if not c["items"]:
            raise HTTPException(status_code=400, detail="Cart is empty.")
        if c["has_rx_items"] and not p.prescription_id:
            raise HTTPException(status_code=400, detail="Rx prescription required.")
        order_no = f"MED-{uuid.uuid4().hex[:8].upper()}"
        q = """INSERT INTO orders (order_number, customer_name, customer_phone, delivery_address,
               subtotal, delivery_fee, discount, total, items_count, prescription_id) VALUES (?,?,?,?,?,?,?,?,?,?)"""
        args = [order_no, p.customer_name, p.customer_phone, p.delivery_address]
        args += [
            c["subtotal"],
            c["delivery_fee"],
            c["discount"],
            c["total"],
            c["items_count"],
            p.prescription_id,
        ]
        conn.execute(q, args)
        conn.execute("DELETE FROM cart_items")
        conn.commit()
        return {
            "success": True,
            "order_number": order_no,
            "total": c["total"],
            "items_count": c["items_count"],
            "delivery_time": "Today, within 2 Hours",
            "message": "Order confirmed and sent to pharmacy dispatch.",
        }


if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
