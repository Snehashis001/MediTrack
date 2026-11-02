# MediTrack — Premium Digital Pharmacy Web Application
> **MCA Web Programming Mini-Project**  
> Built with **Semantic HTML5**, **Modern CSS3**, and **Vanilla JavaScript** as the primary foundation, supported by an optional **Python FastAPI** & **SQLite** full-stack backend.

---

## 1. Project Overview & Architecture

**MediTrack** is an ecommerce healthcare web application designed as an MCA-level Web Programming demonstration. It delivers a commercial-grade, responsive user interface for browsing genuine medicines, filtering by healthcare categories, instant searching, real-time cart pricing with free delivery incentives, prescription file validation, and checkout routing.

### Web Architecture Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    USER WEB BROWSER                          │
│                                                              │
│  [ HTML5 Structure ] ──> Semantic Layout & Native Modals     │
│  [  CSS3 Styling   ] ──> Medical Teal Theme, Grid & Flexbox  │
│  [ Vanilla JS Core ] ──> Dynamic DOM, Cart Math, LocalStorage│
└──────────────────────────────┬───────────────────────────────┘
                               │
                       HTTP REST API / JSON
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                 OPTIONAL FULL-STACK BACKEND                  │
│                                                              │
│  [  Python FastAPI ] ──> Business Logic, Cart, Validation    │
│  [ SQLite Database ] ──> Parameterized Schema & 16 Products  │
│  [ Static Server   ] ──> Single-command web serving (Port 8080)
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Core Web Programming Concepts Demonstrated

### A. HTML5 (Primary Structure)
- **Semantic Structural Elements**: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`.
- **Accessible HTML5 Dialogs**: Native `<dialog>` elements (`#rx-modal`, `#checkout-modal`, `#order-success-modal`) using standard `.showModal()` and `.close()` methods.
- **Form Elements & Validation**:
  - `<input type="search">` with accessible placeholder and ARIA labels.
  - `<input type="file" accept=".pdf,.png,.jpg,.jpeg">` with client-side & server-side validation.
  - `<input type="tel" pattern="[0-9]{10}">` for 10-digit phone verification.
  - `<select>` dropdowns and `<textarea>` controls with proper `required` attributes.
- **Accessibility (a11y)**: `role="dialog"`, `aria-modal="true"`, `aria-live="polite"`, `aria-hidden` attributes.

### B. CSS3 (Design System & Polish)
- **CSS Custom Properties (Variables)**: `:root` design tokens for medical teal (`#083331`, `#0d5c58`), sky-blue (`#0284c7`), coral discount tags (`#f43f5e`), and warm sand background (`#fcfbf9`).
- **CSS Grid Layouts**:
  - Responsive 6-tile Category showcase: `grid-template-columns: repeat(auto-fit, minmax(170px, 1fr))`.
  - Responsive auto-fill Product Grid: `grid-template-columns: repeat(auto-fill, minmax(260px, 1fr))`.
  - Asymmetric Hero split and 4-column Footer grid.
- **CSS Flexbox**: Horizontal sticky navigation, action bars, quantity steppers, bill breakdown rows, badges.
- **Transitions & Animations**: Smooth card lift (`transform: translateY(-4px)`), floating trust badges (`@keyframes float`), and slide-in cart drawer (`translateX(100%)` to `translateX(0)`).
- **Modular Stylesheets**:
  - `style.css`: Design tokens, base typography, sticky header, navigation, and button styles.
  - `hero.css`: Asymmetric hero section, trust metrics, visual image card, and floating animated badges.
  - `components.css`: Category tiles, features grid, product catalogue grid, cards, badges, and pricing.
  - `modals.css`: Slide-out cart drawer, native `<dialog>` modals, and file drag-and-drop zone.
  - `footer.css`: 4-column responsive footer layout, regulatory note, copyright, and toast notifications.

### C. Vanilla JavaScript (Interactivity & Client Logic)
- **DOM Manipulation**: Dynamic rendering of category tiles, product cards, cart drawer items, and modals via template literals and element binding.
- **Event Listeners**: Live search input (`input`), category filtering (`click`), sorting (`change`), modal actions, and slide-out cart drawer toggle.
- **Client Pricing Engine**: Dynamic calculation of Subtotal, MRP Total, Savings Discount, and Delivery Fee ($4.99 or FREE for orders $\ge \$35.00$).
- **State Management & LocalStorage**: Automatic client persistence in `localStorage` (`meditrack_cart`, `meditrack_rx`) ensuring complete standalone functionality even offline.
- **File & Form Validation**: Checking prescription MIME types, extensions, and file sizes $\le 5\text{MB}$.
- **Toast Notifications**: Lightweight, auto-dismissing feedback messages (`showToast`).

### D. Optional Python FastAPI & SQLite Backend
- **RESTful Endpoints**:
  - `GET /api/categories`: Returns categories with item counts.
  - `GET /api/products`: Parameterized search (`search`), category filter (`category`), and sort (`sort`).
  - `GET /api/cart`, `POST /api/cart`, `DELETE /api/cart/{id}`: SQLite-backed cart synchronization.
  - `POST /api/prescriptions/upload`: Validates file size $\le 5\text{MB}$, allowed extensions, saves to `backend/uploads/`.
  - `POST /api/orders`: Enforces prescription presence when cart contains Rx-only drugs (e.g. Amoxicillin), creates order, and clears cart.
- **SQLite Database**: Auto-seeds 16 products across 6 clinical categories on first run (`backend/meditrack.db`).

---

## 3. Project Structure

```
meditrack/
│
├── frontend/
│   ├── index.html        # Semantic HTML5 homepage structure & native dialogs
│   ├── style.css         # CSS3 design tokens, variables, header, nav & buttons
│   ├── hero.css          # Asymmetric hero layout, trust metrics & floating badges
│   ├── components.css    # Category showcase, features & product catalogue cards
│   ├── modals.css        # Slide-out cart drawer, native dialog modals & drop zone
│   ├── footer.css        # Professional footer grid & toast notifications
│   ├── data.js           # Categories metadata & fallback clinical product catalog
│   ├── app.js            # Vanilla JS catalog rendering, live search & category filters
│   └── cart.js           # Vanilla JS cart calculations, prescription upload & checkout
│
├── backend/
│   ├── main.py           # FastAPI REST API & static file serving
│   ├── database.py       # SQLite connection, schema & 16 seed products
│   └── uploads/          # Directory storing validated prescription uploads
│
├── requirements.txt      # Python dependencies (fastapi, uvicorn, python-multipart)
├── run.py                # One-click launcher script for Windows
├── test_app.py           # 12-point automated integration test suite
├── audit_loc.py          # Programmatic LOC auditing script
├── .prettierrc           # Prettier configuration
└── README.md             # Project documentation
```

---

## 5. Installation & Windows Execution

### Step 1: Install Python Dependencies
Open PowerShell or Command Prompt in `E:\meditrack`:
```powershell
pip install -r requirements.txt
```

### Step 2: Run the Server
Execute the launcher script:
```powershell
python run.py
```
Or start via uvicorn directly:
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080 --reload
```

### Step 3: Open in Browser
Visit **`http://127.0.0.1:8080`** in your browser (Google Chrome, Microsoft Edge, Firefox).

> **Standalone Mode**: You can also simply double-click `frontend/index.html` to run MediTrack purely client-side in any browser with full cart, search, and local storage capabilities!

---

## 6. Running Integration Tests

To execute the automated 12-point test suite:
```powershell
python test_app.py
```

### Test Verification Results:
```
============================================================
 MediTrack - Starting Integration Tests
============================================================
  [PASS] GET / -> index.html served successfully  
  [PASS] GET /style.css -> CSS design system served  
  [PASS] GET /app.js -> Vanilla JS app engine served  
  [PASS] GET /api/categories -> Returned 6 categories  
  [PASS] GET /api/products -> Returned 16 medicines  
  [PASS] GET /api/products?category=Vitamins -> Filter verified  
  [PASS] GET /api/products?search=Paracetamol -> Search verified  
  [PASS] GET /api/products?sort=price_asc -> Price sorting verified  
  [PASS] DELETE /api/cart -> Cart initialized/cleared  
  [PASS] POST /api/cart (Subtotal < $35) -> Delivery fee $4.99 calculated correctly
  [PASS] POST /api/cart (Subtotal >= $35) -> FREE delivery threshold verified
  [PASS] POST /api/prescriptions/upload -> Rejected invalid file format (.exe) 
  [PASS] POST /api/prescriptions/upload -> Validated and stored Rx #2  
  [PASS] POST /api/orders -> Rx prescription required check verified 
  [PASS] POST /api/orders -> Order confirmed  
  [PASS] Cart empty verification -> Cart emptied after checkout
============================================================
 ALL 12 INTEGRATION TESTS PASSED SUCCESSFULLY!
============================================================
```

---

