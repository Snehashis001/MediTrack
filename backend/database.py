import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "meditrack.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                generic_name TEXT,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                mrp REAL NOT NULL,
                discount INTEGER DEFAULT 0,
                dosage TEXT,
                rating REAL DEFAULT 4.8,
                reviews_count INTEGER DEFAULT 120,
                in_stock INTEGER DEFAULT 1,
                requires_prescription INTEGER DEFAULT 0,
                image_url TEXT NOT NULL,
                description TEXT,
                is_bestseller INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL UNIQUE,
                quantity INTEGER NOT NULL DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                patient_name TEXT,
                status TEXT DEFAULT 'Verified for Order',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                subtotal REAL NOT NULL,
                delivery_fee REAL NOT NULL,
                discount REAL NOT NULL,
                total REAL NOT NULL,
                items_count INTEGER NOT NULL,
                prescription_id INTEGER,
                payment_method TEXT DEFAULT 'Cash on Delivery',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.execute("SELECT COUNT(*) as count FROM products")
        if cursor.fetchone()["count"] == 0:
            seed_products(conn)


RAW_DATA = """Paracetamol Extra 500mg|Acetaminophen|Pain Relief|6.49|8.99|28|20 Tablets|4.9|342|1|0|https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80|Fast-acting relief for mild-to-moderate fever and headaches.|1|1
Ibuprofen Ultra Softgels 400mg|Ibuprofen NSAID|Pain Relief|9.99|12.99|23|30 Softgels|4.8|218|1|0|https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=600&q=80|Targeted anti-inflammatory action for joint stiffness and sprains.|1|0
Diclofenac Relief Gel|Diclofenac Sodium 1%|Pain Relief|7.50|9.50|21|50g Tube|4.7|140|1|0|https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=600&q=80|Deep-penetrating topical pain gel providing fast localized comfort.|0|1
Vitamin C + Zinc Immunity Fizz|Ascorbic Acid + Zinc|Vitamins|8.99|11.99|25|20 Tablets|4.9|410|1|0|https://images.unsplash.com/photo-1577401239170-897942555fb3?auto=format&fit=crop&w=600&q=80|Zesty orange effervescent tablets providing daily antioxidant defense.|1|1
Vitamin D3 2000 IU + K2|Cholecalciferol + K2|Vitamins|14.50|18.00|19|60 Softgels|4.8|185|1|0|https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=600&q=80|Synergistic duo for strong bone density and cardiovascular support.|0|1
Omega-3 Triple Strength Fish Oil|EPA 600mg + DHA 400mg|Vitamins|16.99|22.00|23|60 Softgels|4.9|290|1|0|https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80|Molecularly distilled wild-caught fish oil for heart and brain health.|1|1
Ceramide Hydrating Daily Cleanser|Ceramides 1, 3, 6-II|Personal Care|13.25|16.50|20|250ml Pump|4.9|520|1|0|https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80|Dermatologist-developed gentle moisturizing face and body wash.|1|0
Medicated Antiseptic Lip Balm SPF 15|Camphor + Menthol|Personal Care|4.25|5.50|23|10g Tube|4.6|95|1|0|https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80|Intense cooling relief and UV protection for chapped, dry lips.|0|0
Digital Smart BP Monitor|Oscillometric Upper Arm|Healthcare Devices|34.99|45.00|22|1 Unit + Cuff|4.8|310|1|0|https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=600&q=80|Clinically accurate automatic upper-arm monitor with irregular heartbeat alert.|1|1
Infrared Forehead Thermometer|Dual Mode Clinical Sensor|Healthcare Devices|22.50|29.99|25|1 Unit|4.7|178|1|0|https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=600&q=80|1-second touch-free temperature reading with multi-color fever indicator.|0|1
Fingertip Pulse Oximeter Pro|SpO2 & Pulse Rate Sensor|Healthcare Devices|18.99|24.99|24|1 Device|4.8|260|1|0|https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=600&q=80|High-contrast OLED display providing instant oxygen saturation and pulse.|0|0
Waterproof Antiseptic Bandages|Sterile Fabric Adhesive|First Aid|5.99|7.50|20|Box of 50|4.8|150|1|0|https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=600&q=80|Breathable water-resistant flexible adhesive strips with non-stick pad.|0|0
Povidone-Iodine Solution 10%|Povidone-Iodine USP|First Aid|6.80|8.50|20|100ml Bottle|4.7|88|1|0|https://images.unsplash.com/photo-1584362917165-526a968579e8?auto=format&fit=crop&w=600&q=80|Broad-spectrum antiseptic solution for topical disinfection of cuts.|0|0
Melatonin 5mg Sleep Gummies|Melatonin + Chamomile|General Wellness|11.99|15.00|20|60 Gummies|4.9|390|1|0|https://images.unsplash.com/photo-1576602976047-174e57a47881?auto=format&fit=crop&w=600&q=80|Non-habit forming botanical sleep gummies for restful nights.|1|1
Organic Ashwagandha KSM-66|Withania Somnifera 600mg|General Wellness|15.50|19.99|22|60 Veg Caps|4.8|220|1|0|https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80|Pure root extract adaptogen formulated to promote stress resilience and energy.|0|1
Amoxicillin Clavulanate 625mg|Amoxicillin + Clavulanic|General Wellness|14.20|18.00|21|10 Tablets|4.9|160|1|1|https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=600&q=80|PRESCRIPTION REQUIRED: Broad-spectrum antibacterial therapy. Valid Rx mandatory.|1|1"""


def seed_products(conn):
    rows = []
    for line in RAW_DATA.strip().split("\n"):
        p = line.split("|")
        rows.append(
            (
                p[0],
                p[1],
                p[2],
                float(p[3]),
                float(p[4]),
                int(p[5]),
                p[6],
                float(p[7]),
                int(p[8]),
                int(p[9]),
                int(p[10]),
                p[11],
                p[12],
                int(p[13]),
                int(p[14]),
            )
        )
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO products (
            name, generic_name, category, price, mrp, discount, dosage,
            rating, reviews_count, in_stock, requires_prescription,
            image_url, description, is_bestseller, is_featured
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        rows,
    )
    conn.commit()
