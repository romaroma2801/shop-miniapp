function initOrderPage() {
  // Создаем HTML структуру
  const orderHTML = `
    <div id="loader" class="loader">
      <img src="/static/Eicon.png" alt="Loading">
    </div>

    <div class="header">
      <img src="/static/logo22.png" alt="Логотип" class="logo">
    </div>

    <div id="order-content">
      <h2 class="order-title">Оформление заказа</h2>
      
      <div class="order-items-container">
        <div id="order-items">
          <!-- Товары будут здесь -->
        </div>
      </div>
      
      <div class="order-summary" id="order-summary">
        <!-- Суммы будут здесь -->
      </div>
      
      <form id="order-form">
        <div class="form-group">
          <label for="last-name">Фамилия</label>
          <input type="text" id="last-name" required>
        </div>
        
        <div class="form-group">
          <label for="first-name">Имя</label>
          <input type="text" id="first-name" required>
        </div>
        
        <div class="form-group">
          <label for="city">Город / Населённый пункт</label>
          <input type="text" id="city" required>
        </div>
        
        <div class="form-group">
          <label for="postcode">Индекс</label>
          <input type="text" id="postcode" required>
        </div>
        
        <div class="form-group">
          <label for="address">Адрес</label>
          <input type="text" id="address" required>
        </div>
        
        <div class="form-group" id="phone-group">
          <label for="phone">Номер телефона</label>
          <input type="tel" id="phone" required>
        </div>
        
        <button type="submit" class="submit-btn">Отправить заказ</button>
      </form>
    </div>
  `;

  // Вставляем HTML в DOM
  showContent(orderHTML);

  // Инициализация страницы
  const loader = document.getElementById('loader');
  const content = document.getElementById('order-content');
  
  if (loader) loader.style.display = 'flex';
  if (content) content.style.display = 'none';

  // Основная инициализация
  const initialize = async () => {
    try {
      const userData = await loadUserData();
      
      // Устанавливаем значения формы
      if (userData) {
        const firstNameInput = document.getElementById('first-name');
        const phoneInput = document.getElementById('phone');
        
        if (firstNameInput) firstNameInput.value = userData.first_name || '';
        if (phoneInput) {
          phoneInput.value = userData.phone || '';
          if (userData.phone) phoneInput.readOnly = true;
        }
      }

      renderOrderItems();
      renderOrderSummary();

      // Обработчик формы
      const form = document.getElementById('order-form');
      if (form) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          await submitOrder();
        });
      }

    } catch (error) {
      console.error('Ошибка инициализации:', error);
      showToast('Ошибка загрузки страницы');
    } finally {
      setTimeout(() => {
        if (loader) loader.style.display = 'none';
        if (content) content.style.display = 'block';
      }, 300);
    }
  };

  // Даем время браузеру обработать DOM
  setTimeout(initialize, 50);
}

function renderOrderItems() {
  const itemsContainer = document.getElementById('order-items');
  if (!itemsContainer) {
    console.error('Контейнер товаров не найден');
    return;
  }

  const items = cart.items;
  
  if (!items.length) {
    itemsContainer.innerHTML = '<p class="empty-cart">Ваша корзина пуста</p>';
    return;
  }

  itemsContainer.innerHTML = items.map(item => `
    <div class="cart-item">
      <div class="cart-item-info">
        <div class="cart-item-title">${item.title}</div>
        ${item.option ? `<div class="cart-item-option">${item.option}</div>` : ''}
        <div class="cart-item-quantity">Количество: ${item.quantity}</div>
      </div>
      <div class="cart-item-right">
        <div class="cart-item-price">${(item.price * item.quantity).toFixed(2)} BYN</div>
        <button class="cart-item-remove" onclick="removeOrderItem('${item.key}', event)">
        </button>
      </div>
    </div>
  `).join('');
}
function removeOrderItem(key, event) {
  event.stopPropagation();
  cart.remove(key);
  renderOrderItems();
  renderOrderSummary();
}

function renderOrderSummary() {
  const summaryContainer = document.getElementById('order-summary');
  const total = cart.getTotal();
  const discount = cart.getDiscount();
  const delivery = total >= 100 ? 0 : 4;
  const finalTotal = total - discount + delivery;

  summaryContainer.innerHTML = `
    <div class="summary-row">
      <span>Скидка 3%:</span>
      <span>-${discount.toFixed(2)} BYN</span>
    </div>
    <div class="summary-row">
      <span>Доставка:</span>
      <span>${delivery.toFixed(2)} BYN ${delivery === 0 ? '<span class="free-delivery">(бесплатно от 100 BYN)</span>' : ''}</span>
    </div>
    <div class="summary-row summary-total">
      <span>Итого к оплате:</span>
      <span>${finalTotal.toFixed(2)} BYN</span>
    </div>
  `;
}

async function loadUserData() {
  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  if (!tgUser) return null;

  const userKey = `user_${tgUser.id}`;
  return JSON.parse(localStorage.getItem(userKey)) || {
    id: tgUser.id,
    username: tgUser.username || `id${tgUser.id}`,
    first_name: tgUser.first_name || '',
    phone: tgUser.phone_number || ''
  };
}

async function submitOrder() {
  const userData = await loadUserData();
  if (!userData) {
    showToast("Ошибка: данные пользователя не загружены");
    return;
  }

  const orderData = {
    items: cart.items,
    total: cart.getTotal(),
    discount: cart.getDiscount(),
    delivery: cart.getTotal() >= 100 ? 0 : 4,
    final_total: cart.getFinalTotal() + (cart.getTotal() >= 100 ? 0 : 4),
    customer_name: `${document.getElementById('last-name').value} ${document.getElementById('first-name').value}`,
    city: document.getElementById('city').value,
    postcode: document.getElementById('postcode').value,
    address: document.getElementById('address').value,
    phone: document.getElementById('phone').value,
    username: userData.username || `id${userData.id}`
  };

  try {
    const response = await fetch('/api/create-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData)
    });

    const result = await response.json();

    if (result.status === 'success') {
      cart.items = [];
      cart.save();
      showUserPage(); // ✅ возвращаемся в личный кабинет
    } else {
      showToast(result.message || "Ошибка при оформлении заказа");
    }
  } catch (error) {
    console.error('Ошибка:', error);
    showToast("Произошла ошибка при отправке заказа");
  }
}

function showToast(message, duration = 2000) {
  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 12px 24px;
    border-radius: 4px;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s;
  `;
  document.body.appendChild(toast);

  setTimeout(() => toast.style.opacity = 1, 10);
  setTimeout(() => {
    toast.style.opacity = 0;
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

window.initOrderPage = initOrderPage;
