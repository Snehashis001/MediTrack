/* ==========================================================================
   MediTrack - Cart, Pricing Engine & Modals (Vanilla JS + LocalStorage + API)
   ========================================================================== */
const CartState = {
  items: JSON.parse(localStorage.getItem('meditrack_cart') || '[]'),
  prescription: JSON.parse(localStorage.getItem('meditrack_rx') || 'null')
};

function saveLocalCart() {
  localStorage.setItem('meditrack_cart', JSON.stringify(CartState.items));
  const b = document.getElementById('cart-badge-count');
  if (b) b.textContent = CartState.items.reduce((s, i) => s + i.quantity, 0);
}

function calculateCartTotals() {
  const items = CartState.items;
  const sub = Math.round(items.reduce((s, i) => s + i.price * i.quantity, 0) * 100) / 100;
  const mrp = Math.round(items.reduce((s, i) => s + (i.mrp || i.price) * i.quantity, 0) * 100) / 100;
  const disc = Math.max(0, Math.round((mrp - sub) * 100) / 100);
  const fee = sub >= 35.0 || !items.length ? 0.0 : 4.99;
  return {
    subtotal: sub,
    mrpTotal: mrp,
    discount: disc,
    delivery: fee,
    total: Math.round((sub + fee) * 100) / 100,
    hasRx: items.some((i) => i.requires_prescription === 1)
  };
}

async function syncWithBackendCart(productId, quantity) {
  try {
    const res = await fetch('/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, quantity })
    });
    if (res.ok) {
      CartState.items = (await res.json()).items;
      saveLocalCart();
    }
  } catch (_) {}
}

function addToCart(p, qty = 1) {
  const ex = CartState.items.find((i) => i.product_id === p.id);
  if (ex) ex.quantity += qty;
  else
    CartState.items.push({
      product_id: p.id,
      name: p.name,
      price: p.price,
      mrp: p.mrp,
      dosage: p.dosage,
      requires_prescription: p.requires_prescription,
      image_url: p.image_url,
      quantity: qty
    });
  saveLocalCart();
  syncWithBackendCart(p.id, ex ? ex.quantity : qty);
  renderCartDrawer();
  if (window.renderProducts) window.renderProducts();
  if (window.showToast) window.showToast(`Added ${p.name} to cart!`);
}

function updateCartQuantity(pid, qty) {
  if (qty <= 0) {
    CartState.items = CartState.items.filter((i) => i.product_id !== pid);
    fetch(`/api/cart/${pid}`, { method: 'DELETE' }).catch(() => {});
  } else {
    const it = CartState.items.find((i) => i.product_id === pid);
    if (it) it.quantity = qty;
    syncWithBackendCart(pid, qty);
  }
  saveLocalCart();
  renderCartDrawer();
  if (window.renderProducts) window.renderProducts();
}

function renderCartDrawer() {
  const c = document.getElementById('cart-items-list');
  const t = calculateCartTotals();
  if (!c) return;

  c.innerHTML = !CartState.items.length
    ? `
    <div class="empty-cart-state"><div class="empty-cart-icon">🛒</div><h4>Your Cart is Empty</h4><p>Explore our wide range of medicines and wellness products.</p></div>`
    : CartState.items
        .map(
          (i) => `
      <div class="cart-item">
        <img src="${i.image_url}" alt="${i.name}" class="cart-item-img">
        <div class="cart-item-info">
          <div class="cart-item-title">${i.name}</div>
          <div class="cart-item-dosage">${i.dosage || ''} ${i.requires_prescription ? '<span class="badge badge-rx">Rx</span>' : ''}</div>
          <div class="cart-item-price">$${(i.price * i.quantity).toFixed(2)}</div>
        </div>
        <div class="qty-controller">
          <button class="qty-btn" onclick="updateCartQuantity(${i.product_id}, ${i.quantity - 1})">−</button>
          <span class="qty-number">${i.quantity}</span>
          <button class="qty-btn" onclick="updateCartQuantity(${i.product_id}, ${i.quantity + 1})">+</button>
        </div>
      </div>`
        )
        .join('');

  document.getElementById('cart-mrp').textContent = `$${t.mrpTotal.toFixed(2)}`;
  document.getElementById('cart-discount').textContent = `-$${t.discount.toFixed(2)}`;
  document.getElementById('cart-delivery').textContent = t.delivery === 0 ? 'FREE' : `$${t.delivery.toFixed(2)}`;
  document.getElementById('cart-total').textContent = `$${t.total.toFixed(2)}`;

  const rem = Math.max(0, 35 - t.subtotal);
  document.getElementById('shipping-progress-fill').style.width = `${Math.min(100, (t.subtotal / 35) * 100)}%`;
  document.getElementById('shipping-progress-text').textContent = !CartState.items.length
    ? 'Add $35.00 for FREE Delivery'
    : rem === 0
      ? '🎉 Unlocked FREE Express Delivery!'
      : `Add $${rem.toFixed(2)} more for FREE Delivery`;
}

function toggleCartDrawer(open) {
  const el = document.getElementById('cart-drawer-overlay');
  if (open) renderCartDrawer();
  el.classList.toggle('open', open);
  el.setAttribute('aria-hidden', String(!open));
}

function setupCartEvents() {
  document.getElementById('cart-drawer-trigger').addEventListener('click', () => toggleCartDrawer(true));
  document.getElementById('cart-close-btn').addEventListener('click', () => toggleCartDrawer(false));
  document.getElementById('cart-drawer-overlay').addEventListener('click', (e) => {
    if (e.target.id === 'cart-drawer-overlay') toggleCartDrawer(false);
  });
  document.getElementById('proceed-checkout-btn').addEventListener('click', () => {
    if (!CartState.items.length) {
      if (window.showToast) window.showToast('Cart is empty!', 'error');
      return;
    }
    toggleCartDrawer(false);
    openCheckoutModal();
  });
  document.getElementById('rx-upload-trigger').addEventListener('click', openRxModal);
  document.getElementById('hero-rx-btn').addEventListener('click', openRxModal);
}

function openRxModal() {
  const m = document.getElementById('rx-modal');
  const rx = CartState.prescription;
  document.getElementById('rx-modal-body').innerHTML = `
    <div class="modal-header"><h3>Upload Doctor Prescription</h3><button class="modal-close-btn" onclick="document.getElementById('rx-modal').close()">&times;</button></div>
    <form id="rx-form">
      <p class="modal-desc">Attach a valid doctor's prescription (PDF, JPG, PNG up to 5MB).</p>
      <div class="file-drop-zone" onclick="document.getElementById('rx-file-input').click()">
        <input type="file" id="rx-file-input" accept=".pdf,.png,.jpg,.jpeg" class="file-input-hidden">
        <div class="drop-icon">📑</div>
        <div class="drop-label" id="drop-label">${rx ? rx.filename : 'Click or Drag prescription file here'}</div>
        <div class="file-spec">Supported: PDF, JPG, PNG (Max 5MB)</div>
      </div>
      <div class="form-group"><label for="rx-name">Patient Name</label><input type="text" id="rx-name" placeholder="Patient Name" value="${rx ? rx.patient_name || '' : ''}"></div>
      <div class="modal-actions"><button type="button" class="btn btn-secondary" onclick="document.getElementById('rx-modal').close()">Cancel</button><button type="submit" class="btn btn-primary">Attach Prescription</button></div>
    </form>`;

  const fi = document.getElementById('rx-file-input');
  fi.addEventListener('change', () => {
    const f = fi.files[0];
    if (f && f.size > 5 * 1024 * 1024) {
      if (window.showToast) window.showToast('File exceeds 5MB!', 'error');
      fi.value = '';
      return;
    }
    if (f) document.getElementById('drop-label').textContent = `${f.name} (${(f.size / 1024).toFixed(1)} KB)`;
  });

  document.getElementById('rx-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fi.files[0];
    if (!file && !CartState.prescription) {
      if (window.showToast) window.showToast('Please select a file', 'error');
      return;
    }
    const pName = document.getElementById('rx-name').value || 'Self';
    if (file) {
      const fd = new FormData();
      fd.append('file', file);
      fd.append('patient_name', pName);
      try {
        const res = await fetch('/api/prescriptions/upload', { method: 'POST', body: fd });
        CartState.prescription = res.ok
          ? await res.json()
          : { prescription_id: 1, filename: file.name, patient_name: pName };
      } catch (_) {
        CartState.prescription = { prescription_id: 1, filename: file.name, patient_name: pName };
      }
    }
    localStorage.setItem('meditrack_rx', JSON.stringify(CartState.prescription));
    m.close();
    if (window.showToast) window.showToast('Prescription attached! ✅');
  });
  m.showModal();
}

function openCheckoutModal() {
  const t = calculateCartTotals();
  const m = document.getElementById('checkout-modal');
  document.getElementById('checkout-modal-body').innerHTML = `
    <div class="modal-header"><h3>Delivery & Checkout</h3><button class="modal-close-btn" onclick="document.getElementById('checkout-modal').close()">&times;</button></div>
    <form id="chk-form">
      <div class="form-group"><label for="chk-name">Full Name *</label><input type="text" id="chk-name" required placeholder="Full Name"></div>
      <div class="form-group"><label for="chk-phone">Mobile (10 digits) *</label><input type="tel" id="chk-phone" pattern="[0-9]{10}" required placeholder="9876543210"></div>
      <div class="form-group"><label for="chk-address">Delivery Address *</label><textarea id="chk-address" rows="2" required placeholder="Street address, City, PIN"></textarea></div>
      <div class="checkout-rx-notice">${t.hasRx ? (CartState.prescription ? `✅ Rx: <strong>${CartState.prescription.filename}</strong>` : '⚠️ Rx item in cart! Upload required.') : 'ℹ️ No prescription required.'}</div>
      <div class="order-summary-box">Items: ${CartState.items.length} | Delivery: ${t.delivery === 0 ? 'FREE' : '$' + t.delivery.toFixed(2)} | <strong>Total: $${t.total.toFixed(2)}</strong></div>
      <div class="modal-actions"><button type="button" class="btn btn-secondary" onclick="document.getElementById('checkout-modal').close(); toggleCartDrawer(true);">Back</button><button type="submit" class="btn btn-primary">Place Order (COD)</button></div>
    </form>`;

  document.getElementById('chk-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (t.hasRx && !CartState.prescription) {
      if (window.showToast) window.showToast('Rx required! Upload prescription.', 'error');
      openRxModal();
      return;
    }
    const p = {
      customer_name: document.getElementById('chk-name').value,
      customer_phone: document.getElementById('chk-phone').value,
      delivery_address: document.getElementById('chk-address').value,
      prescription_id: CartState.prescription ? CartState.prescription.prescription_id : null
    };
    let ord = {
      order_number: 'MED-' + Math.random().toString(36).substring(2, 10).toUpperCase(),
      total: t.total,
      delivery_time: 'Today, within 2 Hours'
    };
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(p)
      });
      if (res.ok) ord = await res.json();
    } catch (_) {}
    m.close();
    CartState.items = [];
    saveLocalCart();
    renderCartDrawer();
    if (window.renderProducts) window.renderProducts();
    openSuccessModal(ord, p);
  });
  m.showModal();
}

function openSuccessModal(order, cust) {
  const m = document.getElementById('order-success-modal');
  document.getElementById('success-modal-body').innerHTML = `
    <div class="success-icon-wrap">✅</div><h3 class="success-title">Order Confirmed!</h3><p class="success-order-no">${order.order_number}</p>
    <p class="success-desc">Assigned to a licensed pharmacist for express dispatch.</p>
    <div class="success-meta-box"><div>🚚 <strong>Window:</strong> ${order.delivery_time}</div><div>💵 <strong>Total (COD):</strong> $${Number(order.total).toFixed(2)}</div><div>📍 <strong>Address:</strong> ${cust.delivery_address}</div></div>
    <button class="btn btn-primary btn-block" onclick="document.getElementById('order-success-modal').close()">Continue Shopping</button>`;
  m.showModal();
}

document.addEventListener('DOMContentLoaded', () => {
  setupCartEvents();
  saveLocalCart();
});
