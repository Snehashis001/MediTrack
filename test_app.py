"""MediTrack Automated Integration Test Suite - Tests live server, SQLite, Cart & APIs."""

import io
import subprocess
import sys
import time

import requests

BASE_URL = "http://127.0.0.1:8080"


def run_tests():
    print("=" * 60)
    print(" MediTrack - Starting Integration Tests")
    print("=" * 60)

    # 1. Test Static Files & HTML
    r_index = requests.get(f"{BASE_URL}/")
    assert r_index.status_code == 200, f"Expected 200, got {r_index.status_code}"
    assert "MediTrack" in r_index.text
    print("  [PASS] GET / -> index.html served successfully (200 OK)")

    r_css = requests.get(f"{BASE_URL}/style.css")
    assert r_css.status_code == 200
    print("  [PASS] GET /style.css -> CSS design system served (200 OK)")

    r_js = requests.get(f"{BASE_URL}/app.js")
    assert r_js.status_code == 200
    print("  [PASS] GET /app.js -> Vanilla JS app engine served (200 OK)")

    # 2. Test Categories
    r_cat = requests.get(f"{BASE_URL}/api/categories")
    assert r_cat.status_code == 200
    cats = r_cat.json()
    assert len(cats) >= 6
    cat_names = [c["category"] for c in cats]
    assert "Pain Relief" in cat_names
    assert "Vitamins" in cat_names
    print(f"  [PASS] GET /api/categories -> Returned {len(cats)} categories (200 OK)")

    # 3. Test Products Listing & Search & Sort
    r_prod = requests.get(f"{BASE_URL}/api/products")
    assert r_prod.status_code == 200
    products = r_prod.json()
    assert len(products) >= 16
    print(f"  [PASS] GET /api/products -> Returned {len(products)} medicines (200 OK)")

    # Filter
    r_vit = requests.get(f"{BASE_URL}/api/products?category=Vitamins")
    assert r_vit.status_code == 200
    assert all(p["category"] == "Vitamins" for p in r_vit.json())
    print("  [PASS] GET /api/products?category=Vitamins -> Filter verified (200 OK)")

    # Search
    r_search = requests.get(f"{BASE_URL}/api/products?search=Paracetamol")
    assert r_search.status_code == 200
    assert any("Paracetamol" in p["name"] for p in r_search.json())
    print("  [PASS] GET /api/products?search=Paracetamol -> Search verified (200 OK)")

    # Sort
    r_sort = requests.get(f"{BASE_URL}/api/products?sort=price_asc")
    assert r_sort.status_code == 200
    prices = [p["price"] for p in r_sort.json()]
    assert prices == sorted(prices)
    print(
        "  [PASS] GET /api/products?sort=price_asc -> Price sorting verified (200 OK)"
    )

    # 4. Test Cart Management & Calculations
    requests.delete(f"{BASE_URL}/api/cart")
    r_cart_empty = requests.get(f"{BASE_URL}/api/cart").json()
    assert r_cart_empty["items_count"] == 0
    assert r_cart_empty["total"] == 0.0
    print("  [PASS] DELETE /api/cart -> Cart initialized/cleared (200 OK)")

    # Add Paracetamol ($6.49) -> Subtotal $6.49 < $35 -> Delivery Fee $4.99
    r_add1 = requests.post(
        f"{BASE_URL}/api/cart", json={"product_id": 1, "quantity": 1}
    )
    assert r_add1.status_code == 200
    c1 = r_add1.json()
    assert c1["items_count"] == 1
    assert c1["subtotal"] == 6.49
    assert c1["delivery_fee"] == 4.99
    assert c1["total"] == 11.48
    print(
        "  [PASS] POST /api/cart (Subtotal < $35) -> Delivery fee $4.99 calculated correctly"
    )

    # Add BP Monitor ($34.99) -> Subtotal $6.49 + $34.99 = $41.48 >= $35 -> Delivery Fee $0.00 FREE!
    r_add2 = requests.post(
        f"{BASE_URL}/api/cart", json={"product_id": 9, "quantity": 1}
    )
    assert r_add2.status_code == 200
    c2 = r_add2.json()
    assert c2["items_count"] == 2
    assert c2["subtotal"] == 41.48
    assert c2["delivery_fee"] == 0.0
    assert c2["total"] == 41.48
    print(
        "  [PASS] POST /api/cart (Subtotal >= $35) -> FREE delivery threshold verified"
    )

    # 5. Prescription File Validation
    # Reject .exe
    r_bad = requests.post(
        f"{BASE_URL}/api/prescriptions/upload",
        files={
            "file": ("virus.exe", io.BytesIO(b"binary"), "application/octet-stream")
        },
    )
    assert r_bad.status_code == 400
    print(
        "  [PASS] POST /api/prescriptions/upload -> Rejected invalid file format (.exe) (400 Bad Request)"
    )

    # Accept .pdf
    r_good = requests.post(
        f"{BASE_URL}/api/prescriptions/upload",
        files={
            "file": (
                "rx_document.pdf",
                io.BytesIO(b"%PDF-1.4 Mock Rx"),
                "application/pdf",
            )
        },
        data={"patient_name": "Test Patient"},
    )
    assert r_good.status_code == 200
    rx_info = r_good.json()
    assert rx_info["success"] is True
    rx_id = rx_info["prescription_id"]
    print(
        f"  [PASS] POST /api/prescriptions/upload -> Validated and stored Rx #{rx_id} (200 OK)"
    )

    # 6. Prescription Enforcement on Checkout
    # Add Amoxicillin (requires_prescription = 1)
    requests.post(f"{BASE_URL}/api/cart", json={"product_id": 16, "quantity": 1})
    cart_with_rx = requests.get(f"{BASE_URL}/api/cart").json()
    assert cart_with_rx["has_rx_items"] is True

    # Order without prescription must be rejected
    r_ord_bad = requests.post(
        f"{BASE_URL}/api/orders",
        json={
            "customer_name": "Alice",
            "customer_phone": "9876543210",
            "delivery_address": "42 Pine Street",
        },
    )
    assert r_ord_bad.status_code == 400
    print(
        "  [PASS] POST /api/orders -> Rx prescription required check verified (400 Bad Request)"
    )

    # Order with prescription succeeds
    r_ord_good = requests.post(
        f"{BASE_URL}/api/orders",
        json={
            "customer_name": "Alice",
            "customer_phone": "9876543210",
            "delivery_address": "42 Pine Street",
            "prescription_id": rx_id,
        },
    )
    assert r_ord_good.status_code == 200
    order_res = r_ord_good.json()
    assert order_res["success"] is True
    assert order_res["order_number"].startswith("MED-")
    print(
        f"  [PASS] POST /api/orders -> Order {order_res['order_number']} confirmed (200 OK)"
    )

    # Cart must be cleared after order
    cart_final = requests.get(f"{BASE_URL}/api/cart").json()
    assert cart_final["items_count"] == 0
    print("  [PASS] Cart empty verification -> Cart emptied after checkout")

    print("=" * 60)
    print(" ALL 12 INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("=" * 60)


if __name__ == "__main__":
    p = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8080",
        ]
    )
    try:
        time.sleep(2)
        run_tests()
    finally:
        p.terminate()
