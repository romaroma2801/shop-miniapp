function initFooter() {
  const setActiveFooter = (section) => {
    document.querySelectorAll('.footer-item').forEach(item => {
      item.classList.toggle('active', item.dataset.section === section);
    });
  };

  const goHome = () => {
    setActiveFooter('home');
    window.goHome();
  };

  const showPromotions = () => {
    setActiveFooter('promotions');
    window.showSection('promotions');
  };

  const toggleCart = () => {
    setActiveFooter('cart');
    cart.toggle();
  };

  const handleLogin = () => {
    const user = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if (user) {
      showUserPage(); // ✅ Загрузка кабинета без перехода
    } else {
      Telegram.WebApp.openTelegramLink('https://t.me/Shop_NEKURIBY_bot?start=login');
    }
  };


  document.addEventListener('DOMContentLoaded', initFooter);
  document.getElementById('home-button')?.addEventListener('click', goHome);
  document.getElementById('catalog-button')?.addEventListener('click', () => {
    setActiveFooter('catalog');
    window.showSection('catalog');
  });
  document.getElementById('cart-footer-button')?.addEventListener('click', toggleCart);
  document.getElementById('promotions-button')?.addEventListener('click', () => {
    setActiveFooter('promotions');
    window.showSection('promotions');
  });
  document.getElementById('login-button')?.addEventListener('click', () => {
    setActiveFooter('user');
    window.showUserPage();
  });


  // Инициализация корзины при загрузке
  initCart();
  setActiveFooter('home');
}

function initCart() {
  // Создаем HTML корзины если его нет
  if (!document.getElementById('cart-overlay')) {
    document.body.insertAdjacentHTML('beforeend', `
      <div id="cart-overlay" class="cart-overlay">
        <div class="cart-header">
          Ваша корзина
        </div>
        <div class="cart-content" id="cart-items">
          <!-- Товары будут здесь -->
        </div>
        <div class="cart-summary">
          <div class="cart-summary-row">
            <span>Скидка 3% за регистрацию</span>
            <span id="cart-discount">-0.00 BYN</span>
          </div>
          <div class="cart-summary-row cart-summary-total">
            <span>Итого:</span>
            <span id="cart-total">0.00 BYN</span>
          </div>
          <button class="cart-checkout-btn">Оформить заказ</button>
        </div>
      </div>
    `);
  }
  
  // Инициализация корзины
  cart.updateBadge();
  
  // Закрытие корзины при клике вне ее
  document.addEventListener('click', (event) => {
    const cartOverlay = document.getElementById('cart-overlay');
    if (!cartOverlay || !cartOverlay.classList.contains('show')) return;
    
    const isClickInside = cartOverlay.contains(event.target);
    const isCartButton = event.target.closest('#cart-footer-button');
    
    if (!isClickInside && !isCartButton) {
      cartOverlay.classList.remove('show');
    }
  });
}

// Объект корзины (перенесён из cart.js с небольшими изменениями)
const cart = {
  items: JSON.parse(localStorage.getItem('cart') || '[]'),

  save() {
    localStorage.setItem('cart', JSON.stringify(this.items));
    this.updateBadge();
  },

  add(product, option = null) {
    const key = product.id + '_' + product.title + (option ? `_${option.replace(/\s+/g, '_')}` : '');
    const existingItem = this.items.find(item => item.key === key);
    
    if (existingItem) {
      existingItem.quantity++;
    } else {
      this.items.push({
        key,
        id: product.id,
        title: product.title,
        price: parseFloat(product.special_price || product.price || product.regular_price),
        option,
        quantity: 1,
        optionName: option
      });
    }
    
    this.save();
    this.animateAdd();
    this.render();
  },

  remove(key, event) {
    if (event) event.stopPropagation();
    this.items = this.items.filter(item => item.key !== key);
    this.save();
    this.render();
  },

  getTotal() {
    return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
  },

  getDiscount() {
    return this.getTotal() * 0.03;
  },

  getFinalTotal() {
    return this.getTotal() - this.getDiscount();
  },

  updateBadge() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    
    const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
    badge.textContent = totalItems;
    badge.style.display = totalItems > 0 ? 'flex' : 'none';
  },

  render() {
    const cartItems = document.getElementById('cart-items');
    const cartDiscount = document.getElementById('cart-discount');
    const cartTotal = document.getElementById('cart-total');
    
    if (!cartItems || !cartDiscount || !cartTotal) return;
    
    cartItems.innerHTML = this.items.map(item => `
      <div class="cart-item">
        <div class="cart-item-info">
          <div class="cart-item-title">${item.title}</div>
          ${item.option ? `<div class="cart-item-option">${item.option}</div>` : ''}
          <div class="cart-item-quantity">Количество: ${item.quantity}</div>
        </div>
        <div class="cart-item-right">
          <div class="cart-item-price">${(item.price * item.quantity).toFixed(2)} BYN</div>
          <button class="cart-item-remove" onclick="cart.remove('${item.key}', event)"></button>
        </div>
      </div>
    `).join('');
    
    cartDiscount.textContent = `-${this.getDiscount().toFixed(2)} BYN`;
    cartTotal.textContent = `${this.getFinalTotal().toFixed(2)} BYN`;
    
    const checkoutBtn = document.querySelector('.cart-checkout-btn');
    if (checkoutBtn) {
      checkoutBtn.addEventListener('click', () => {
        if (this.items.length === 0) {
          showToast("Ваша корзина пуста");
          return;
        }
        window.location.href = '/order';
      });
    }
  },

  toggle() {
    const cartOverlay = document.getElementById('cart-overlay');
    if (!cartOverlay) return;
    
    cartOverlay.classList.toggle('show');
    
    if (cartOverlay.classList.contains('show')) {
      this.render();
    }
  },

  animateAdd() {
    const cartButton = document.getElementById('cart-footer-button');
    const badge = document.getElementById('cart-badge');
    
    if (!cartButton || !badge || !event || !event.target) return;
    
    const fly = document.createElement('div');
    fly.className = 'cart-fly';
    document.body.appendChild(fly);
    
    const buttonRect = event.target.getBoundingClientRect();
    const startX = buttonRect.left + buttonRect.width / 2;
    const startY = buttonRect.top + buttonRect.height / 2;
    
    const badgeRect = badge.getBoundingClientRect();
    const endX = badgeRect.left + badgeRect.width / 2;
    const endY = badgeRect.top + badgeRect.height / 2;
    
    fly.style.left = `${startX - 6}px`;
    fly.style.top = `${startY - 6}px`;
    
    const animation = fly.animate([
      { transform: `translate(0, 0) scale(1)` },
      { transform: `translate(${endX - startX}px, ${endY - startY - 50}px) scale(1.5)` },
      { transform: `translate(${endX - startX}px, ${endY - startY}px) scale(1)` }
    ], {
      duration: 600,
      easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    });
    
    animation.onfinish = () => {
      fly.remove();
      badge.classList.add('pulse');
      setTimeout(() => badge.classList.remove('pulse'), 300);
      this.updateBadge();
    };
  }
};

// Делаем корзину доступной глобально
window.cart = cart;
