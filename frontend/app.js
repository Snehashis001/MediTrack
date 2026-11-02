/* ==========================================================================
   MediTrack - Catalog Engine, Live Search & Category Filtering
   ========================================================================== */
const AppState = {
  products: typeof FALLBACK_PRODUCTS !== 'undefined' ? [...FALLBACK_PRODUCTS] : [],
  selectedCategory: 'All',
  searchTerm: '',
  sortOrder: 'default'
};

async function loadProducts() {
  try {
    const res = await fetch('/api/products');
    if (res.ok) AppState.products = await res.json();
  } catch (_) {}
  renderCategories();
  renderProducts();
}

function renderCategories() {
  const grid = document.getElementById('category-grid');
  if (!grid || typeof CATEGORIES === 'undefined') return;
  grid.innerHTML = CATEGORIES.map(
    (c) => `
    <div class="category-card ${AppState.selectedCategory === c.name ? 'active' : ''}" data-category="${c.name}">
      <div class="category-card-icon">${c.icon}</div>
      <div class="category-card-title">${c.name}</div>
      <div class="category-card-count">${c.count} Products</div>
    </div>`
  ).join('');

  grid.querySelectorAll('.category-card').forEach((card) => {
    card.addEventListener('click', () => {
      AppState.selectedCategory = AppState.selectedCategory === card.dataset.category ? 'All' : card.dataset.category;
      renderCategories();
      renderProducts();
      document.getElementById('catalogue').scrollIntoView({ behavior: 'smooth' });
    });
  });
}

function getFilteredProducts() {
  const list = AppState.products.filter((p) => {
    const matchCat = AppState.selectedCategory === 'All' || p.category === AppState.selectedCategory;
    const term = AppState.searchTerm.toLowerCase();
    const matchSearch =
      !term ||
      p.name.toLowerCase().includes(term) ||
      p.generic_name.toLowerCase().includes(term) ||
      p.description.toLowerCase().includes(term);
    return matchCat && matchSearch;
  });

  const sorts = {
    price_asc: (a, b) => a.price - b.price,
    price_desc: (a, b) => b.price - a.price,
    rating: (a, b) => b.rating - a.rating,
    name: (a, b) => a.name.localeCompare(b.name),
    default: (a, b) => (b.is_bestseller || 0) - (a.is_bestseller || 0)
  };
  return list.sort(sorts[AppState.sortOrder] || sorts.default);
}

function renderProducts() {
  const grid = document.getElementById('product-grid');
  const countEl = document.getElementById('results-count');
  const catInd = document.getElementById('active-category-indicator');
  if (!grid) return;

  const filtered = getFilteredProducts();
  if (countEl) countEl.textContent = `${filtered.length} products found`;
  if (catInd) catInd.textContent = AppState.selectedCategory === 'All' ? 'All Products' : AppState.selectedCategory;

  if (!filtered.length) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 3rem 1rem; color: var(--slate-500);">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🔍</div>
        <h3>No matching medicines found</h3>
        <p>Try clearing your search term or selecting a different category.</p>
      </div>`;
    return;
  }

  grid.innerHTML = filtered
    .map((p) => {
      const it = typeof CartState !== 'undefined' ? CartState.items.find((i) => i.product_id === p.id) : null;
      return `
      <article class="product-card" data-id="${p.id}">
        <div class="product-image-wrap">
          <img src="${p.image_url}" alt="${p.name}" class="product-img" loading="lazy">
          <div class="product-badges">
            ${p.discount ? `<span class="badge badge-discount">-${p.discount}%</span>` : ''}
            ${p.requires_prescription ? '<span class="badge badge-rx">Rx</span>' : '<span class="badge badge-otc">OTC</span>'}
          </div>
        </div>
        <div class="product-details">
          <div class="product-category">${p.category}</div>
          <h3 class="product-title">${p.name}</h3>
          <div class="product-generic">${p.generic_name}</div>
          <div class="product-dosage">${p.dosage}</div>
          <div class="product-card-bottom">
            <div class="product-pricing">
              <span class="current-price">$${p.price.toFixed(2)}</span>
              ${p.mrp ? `<span class="mrp-price">$${p.mrp.toFixed(2)}</span>` : ''}
              <span class="rating-pill">★ ${p.rating}</span>
            </div>
            ${
              it
                ? `
              <div class="qty-controller">
                <button class="qty-btn" onclick="updateCartQuantity(${p.id}, ${it.quantity - 1})">−</button>
                <span class="qty-number">${it.quantity} in Cart</span>
                <button class="qty-btn" onclick="updateCartQuantity(${p.id}, ${it.quantity + 1})">+</button>
              </div>`
                : `
              <button class="btn-add-cart" onclick="addToCart(AppState.products.find(x => x.id === ${p.id}))">
                <span>✚</span> Add to Cart
              </button>`
            }
          </div>
        </div>
      </article>`;
    })
    .join('');
}

function showToast(msg, type = 'info') {
  const c = document.getElementById('toast-container');
  if (!c) return;
  const t = document.createElement('div');
  t.className = `toast ${type === 'error' ? 'toast-error' : ''}`;
  t.innerHTML = `<span>${type === 'error' ? '⚠️' : '✓'}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

function setupAppEvents() {
  const search = document.getElementById('global-search');
  if (search) {
    search.addEventListener('input', (e) => {
      AppState.searchTerm = e.target.value.trim();
      renderProducts();
    });
  }

  const sort = document.getElementById('sort-select');
  if (sort) {
    sort.addEventListener('change', (e) => {
      AppState.sortOrder = e.target.value;
      renderProducts();
    });
  }

  const reset = document.getElementById('reset-category-btn');
  if (reset) {
    reset.addEventListener('click', () => {
      AppState.selectedCategory = 'All';
      AppState.searchTerm = '';
      if (search) search.value = '';
      renderCategories();
      renderProducts();
      document.getElementById('catalogue').scrollIntoView({ behavior: 'smooth' });
    });
  }

  document.getElementById('hero-shop-btn').addEventListener('click', () => {
    document.getElementById('catalogue').scrollIntoView({ behavior: 'smooth' });
  });

  document.querySelectorAll('.footer-col a[data-cat]').forEach((l) => {
    l.addEventListener('click', (e) => {
      e.preventDefault();
      AppState.selectedCategory = l.dataset.cat;
      renderCategories();
      renderProducts();
      document.getElementById('catalogue').scrollIntoView({ behavior: 'smooth' });
    });
  });
}

window.renderProducts = renderProducts;
window.showToast = showToast;

document.addEventListener('DOMContentLoaded', () => {
  setupAppEvents();
  loadProducts();
});
