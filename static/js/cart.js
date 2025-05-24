// static/js/cart.js

// Инициализация корзины
const cart = {
  items: JSON.parse(localStorage.getItem('cart') || '[]'),

  save() {
    localStorage.setItem('cart', JSON.stringify(this.items));
    this.updateIcon();
  },

  add(item) {
    const key = item.id + (item.option ? `_${item.option}` : '');
    const existing = this.items.find(i => i.key === key);
    
    if (existing) {
      existing.qty++;
    } else {
      this.items.push({ 
        ...item, 
        key, 
        qty: 1,
        price: parseFloat(item.price)
      });
    }
    
    this.save();
    this.animateAdd();
  },

  remove(key) {
    this.items = this.items.filter(i => i.key !== key);
    this.save();
    this.render();
  },

  getTotal() {
    return this.items.reduce((sum, i) => sum + (i.price * i.qty), 0);
  },

  getDiscount() {
    return this.getTotal() * 0.03;
  },

  getFinalTotal() {
    return this.getTotal() - this.getDiscount();
  },

  updateIcon() {
    const counter = document.getElementById('cart-count');
    if (!counter) return;
    
    const totalQty = this.items.reduce((sum, i) => sum + i.qty, 0);
    counter.textContent = totalQty;
    counter.style.display = totalQty ? 'flex' : 'none';
  },

  render() {
    const panel = document.getElementById('cart-panel');
    if (!panel) return;
    
    const list = document.getElementById('cart-items');
    const discountEl = document.getElementById('cart-discount');
    const totalEl = document.getElementById('cart-total');

    list.innerHTML = this.items.map(item => `
      <div class="cart-item">
        <div>
          <div class="cart-title">${item.title}</div>
          ${item.option ? `<div class="cart-option">${item.option}</div>` : ''}
        </div>
        <div class="cart-price">${(item.price * item.qty).toFixed(2)} BYN</div>
        <button class="remove-button" onclick="cart.remove('${item.key}')">
          <img src="/static/remove.png" alt="Удалить">
        </button>
      </div>
    `).join('');

    discountEl.textContent = `-${this.getDiscount().toFixed(2)} BYN`;
    totalEl.textContent = `${this.getFinalTotal().toFixed(2)} BYN`;
  },

  toggle() {
    const panel = document.getElementById('cart-panel');
    if (!panel) return;
    
    const shown = panel.classList.toggle('show');
    if (shown) this.render();
  },

  animateAdd() {
    const cartIcon = document.querySelector('.cart-button');
    const badge = document.getElementById('cart-count');
    if (!cartIcon || !badge || !event.target) return;

    const ball = document.createElement('div');
    ball.className = 'cart-fly';
    document.body.appendChild(ball);

    const startRect = event.target.getBoundingClientRect();
    const endRect = badge.getBoundingClientRect();
    
    // Начальная позиция (центр кнопки "Купить")
    const startX = startRect.left + startRect.width / 2;
    const startY = startRect.top + startRect.height / 2;
    
    // Конечная позиция (центр бейджа)
    const endX = endRect.left + endRect.width / 2;
    const endY = endRect.top + endRect.height / 2;

    ball.style.left = `${startX - 6}px`;
    ball.style.top = `${startY - 6}px`;

    const animation = ball.animate([
      { transform: `translate(0, 0) scale(1)` },
      { transform: `translate(${endX - startX}px, ${endY - startY - 50}px) scale(1.5)` },
      { transform: `translate(${endX - startX}px, ${endY - startY}px) scale(1)` }
    ], {
      duration: 600,
      easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    });

    animation.onfinish = () => {
      ball.remove();
      badge.classList.add('pulse');
      setTimeout(() => badge.classList.remove('pulse'), 300);
      this.updateIcon();
    };
  }
};

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
  // Вставка HTML корзины если его нет
  if (!document.getElementById('cart-panel')) {
    const panelHTML = `
      <div id="cart-panel" class="cart-slide">
        <div class="cart-header">
          Ваша корзина
          <button class="close-cart" onclick="cart.toggle()">×</button>
        </div>
        <div class="cart-content">
          <div id="cart-items"></div>
        </div>
        <div class="cart-summary">
          <div class="row">
            <span>Скидка 3%</span>
            <span id="cart-discount">-0.00 BYN</span>
          </div>
          <div class="row total">
            <span>Итого:</span>
            <span id="cart-total">0.00 BYN</span>
          </div>
          <button class="checkout-btn">Оформить заказ</button>
        </div>
      </div>
      
      <div class="cart-button-container">
        <button class="cart-button" onclick="cart.toggle()">
          <img src="/static/shop.svg" alt="Корзина">
          <span id="cart-count" class="cart-count-badge"></span>
        </button>
      </div>`;
    
    document.body.insertAdjacentHTML('beforeend', panelHTML);
  }

  // Инициализация корзины
  cart.updateIcon();
  
  // Закрытие корзины при клике вне ее
  document.addEventListener('click', (e) => {
    const panel = document.getElementById('cart-panel');
    if (!panel || !panel.classList.contains('show')) return;
    
    const isCartButton = e.target.closest('.cart-button');
    const isInsideCart = e.target.closest('#cart-panel');
    
    if (!isInsideCart && !isCartButton) {
      panel.classList.remove('show');
    }
  });
});

// Экспорт в глобальную область видимости
window.cart = cart;
