
// Инициализация корзины
const cart = {
  items: JSON.parse(localStorage.getItem('cart') || '[]'),

  save() {
    localStorage.setItem('cart', JSON.stringify(this.items));
    renderCartIcon();
  },

  add(item) {
    const key = item.id + (item.option ? `_${item.option}` : '');
    const existing = this.items.find(i => i.key === key);
    if (existing) existing.qty++;
    else this.items.push({ ...item, key, qty: 1 });
    this.save();
    animateAddToCart();
  },

  remove(key) {
    this.items = this.items.filter(i => i.key !== key);
    this.save();
    renderCart();
  },

  getTotal() {
    return this.items.reduce((sum, i) => sum + i.price * i.qty, 0);
  },

  getDiscount() {
    return this.getTotal() * 0.03;
  },

  getFinalTotal() {
    return this.getTotal() - this.getDiscount();
  }
};

function renderCartIcon() {
  const counter = document.getElementById('cart-count');
  if (!counter) return;
  const totalQty = cart.items.reduce((sum, i) => sum + i.qty, 0);
  counter.textContent = totalQty;
  counter.style.display = totalQty ? 'block' : 'none';
}

function renderCart() {
  const panel = document.getElementById('cart-panel');
  const list = document.getElementById('cart-items');
  const discountEl = document.getElementById('cart-discount');
  const totalEl = document.getElementById('cart-total');

  list.innerHTML = cart.items.map(item => `
    <div class="cart-item">
      <div class="cart-title">
        ${item.title}${item.option ? ` (${item.option})` : ''}
      </div>
      <div class="cart-price">${item.price.toFixed(2)} BYN</div>
      <button class="remove-button" onclick="cart.remove('${item.key}')">
        <img src="/static/remove.png" alt="Удалить">
      </button>
    </div>
  `).join('');

  discountEl.textContent = `-${cart.getDiscount().toFixed(2)} BYN`;
  totalEl.textContent = `${cart.getFinalTotal().toFixed(2)} BYN`;
}

function toggleCart() {
  const panel = document.getElementById('cart-panel');
  const shown = panel.classList.toggle('show');
  if (shown) renderCart();
}

function animateAddToCart() {
  const cartIcon = document.querySelector('.cart-button');
  const badge = document.getElementById('cart-count');
  if (!cartIcon || !badge) return;

  const ball = document.createElement('div');
  ball.className = 'cart-fly';
  document.body.appendChild(ball);

  const rectStart = event.target.getBoundingClientRect();
  const rectEnd = badge.getBoundingClientRect();
  ball.style.left = rectStart.left + 'px';
  ball.style.top = rectStart.top + 'px';

  ball.animate([
    { transform: `translate(0, 0)` },
    { transform: `translate(${rectEnd.left - rectStart.left}px, ${rectEnd.top - rectStart.top}px)` }
  ], {
    duration: 500,
    easing: 'ease-in-out'
  });

  setTimeout(() => {
    ball.remove();
    badge.classList.add('pulse');
    setTimeout(() => badge.classList.remove('pulse'), 300);
    renderCartIcon();
  }, 500);
}

// Вставка панели корзины
if (!document.getElementById('cart-panel')) {
  const panelHTML = `
    <div id="cart-panel" class="cart-slide">
      <div class="cart-content">
        <h3>Добавленные товары</h3>
        <div id="cart-items"></div>
        <div class="cart-summary">
          <div class="row">
            <span>Скидка 3% за регистрацию</span>
            <span id="cart-discount">-0.00 BYN</span>
          </div>
          <div class="row total">
            <span>Итого:</span>
            <span id="cart-total">0.00 BYN</span>
          </div>
          <button class="checkout-btn" disabled>Оформить заказ (в разработке)</button>
        </div>
      </div>
    </div>`;
  document.body.insertAdjacentHTML('beforeend', panelHTML);
}
