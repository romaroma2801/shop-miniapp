function initOrderPage() {
  const loader = document.getElementById('loader');
  const content = document.getElementById('order-content');
  
  if (loader) loader.style.display = 'flex';
  if (content) content.style.display = 'none';

  const maxAttempts = 10;
  let attempts = 0;

  const checkContainers = () => {
    attempts++;
    const itemsContainer = document.getElementById('order-items');
    const summaryContainer = document.getElementById('order-summary');
    const form = document.getElementById('order-form');

    if (itemsContainer && summaryContainer && form) {
      initializePage();
    } else if (attempts < maxAttempts) {
      setTimeout(checkContainers, 100);
    } else {
      console.error('Не удалось найти необходимые элементы');
      showToast('Ошибка загрузки страницы');
      if (loader) loader.style.display = 'none';
      cart.toggle();
    }
  };

  const initializePage = async () => {
    try {
      const userData = await loadUserData();
      
      // Установка значений формы
      const setValue = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.value = value || '';
      };

      if (userData) {
        setValue('first-name', userData.first_name);
        setValue('phone', userData.phone);
        
        const phoneInput = document.getElementById('phone');
        if (phoneInput && userData.phone) {
          phoneInput.readOnly = true;
        }
      }

      renderOrderItems();
      renderOrderSummary();

      // Обработчик формы
      document.getElementById('order-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitOrder();
      });

    } catch (error) {
      console.error('Ошибка инициализации:', error);
      showToast('Ошибка загрузки данных');
    } finally {
      if (loader) loader.style.display = 'none';
      if (content) content.style.display = 'block';
    }
  };

  checkContainers();
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
          <img src="/static/remove.png" alt="Удалить">
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
